import requests
import time
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Union
from modules.performance_optimizer import PerformanceOptimizer, rate_limit_decorator, CircuitBreaker

class TikTokAPI:
    """
    Classe para interagir com a API do TikTok.
    Fornece métodos para autenticação e requisições à API do TikTok.
    """
    
    def __init__(self, cache_manager=None, performance_optimizer=None):
        """
        Inicializa a API do TikTok com as credenciais necessárias.
        
        Args:
            cache_manager: Gerenciador de cache opcional para armazenar respostas
            performance_optimizer: Otimizador de performance opcional
        """
        load_dotenv()
        self.client_key = os.getenv('TIKTOK_CLIENT_KEY')
        self.client_secret = os.getenv('TIKTOK_CLIENT_SECRET')
        self.access_token = os.getenv('TIKTOK_ACCESS_TOKEN')
        
        self.base_url = 'https://open-api.tiktok.com/platform/oauth/connect'
        self.api_url = 'https://open.tiktokapis.com/v2'
        
        self.rate_limit_remaining = 100  # Valor padrão, será atualizado com as respostas
        self.rate_limit_reset = 0
        
        self.cache_manager = cache_manager
        
        # Inicializa o otimizador de performance
        if performance_optimizer:
            self.performance_optimizer = performance_optimizer
        else:
            self.performance_optimizer = PerformanceOptimizer(
                max_retries=3,
                backoff_factor=0.5,
                timeout=30
            )
        
        # Configura circuit breaker para requisições
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=120,  # 2 minutos
            expected_exception=requests.exceptions.RequestException
        )
        
        self.session = self.performance_optimizer.session
    
    def _get_auth_headers(self) -> Dict[str, str]:
        """
        Retorna os cabeçalhos de autenticação para as requisições à API.
        
        Returns:
            Dict[str, str]: Cabeçalhos de autenticação
        """
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def _handle_rate_limit(self, response: requests.Response) -> None:
        """
        Atualiza informações de rate limit com base nos cabeçalhos da resposta.
        
        Args:
            response: Objeto de resposta do requests
        """
        if 'X-RateLimit-Remaining' in response.headers:
            self.rate_limit_remaining = int(response.headers['X-RateLimit-Remaining'])
        
        if 'X-RateLimit-Reset' in response.headers:
            self.rate_limit_reset = int(response.headers['X-RateLimit-Reset'])
        
        # Se estiver próximo do limite, aguarde
        if self.rate_limit_remaining < 5:
            current_time = int(time.time())
            sleep_time = max(0, self.rate_limit_reset - current_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
    
    @rate_limit_decorator(calls_per_minute=25)  # TikTok permite mais requisições
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None, 
                     use_cache: bool = True, cache_ttl: int = 3600) -> Dict:
        """
        Realiza uma requisição à API do TikTok com tratamento de erros e cache otimizado.
        
        Args:
            method: Método HTTP (GET, POST, etc)
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            data: Dados para enviar no corpo da requisição
            use_cache: Se deve usar o cache
            cache_ttl: Tempo de vida do cache em segundos
            
        Returns:
            Dict: Resposta da API em formato JSON
            
        Raises:
            Exception: Erro na requisição à API
        """
        url = f"{self.api_url}/{endpoint}"
        headers = self._get_auth_headers()
        
        # Verificar cache se disponível e solicitado
        if self.cache_manager and use_cache and method.upper() == 'GET':
            cached_data = self.cache_manager.get('tiktok', endpoint, params, 'default')
            if cached_data:
                return cached_data.get('data')
        
        # Verificar rate limit antes da requisição
        if self.rate_limit_remaining < 5:
            current_time = int(time.time())
            sleep_time = max(0, self.rate_limit_reset - current_time)
            if sleep_time > 0:
                time.sleep(sleep_time)
        
        @self.circuit_breaker
        def _make_optimized_request():
            """Função interna para fazer a requisição com circuit breaker"""
            return self.performance_optimizer.make_optimized_request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data,
                timeout=30
            )
        
        try:
            response = _make_optimized_request()
            
            # Atualizar informações de rate limit
            self._handle_rate_limit(response)
            
            # Verificar erros
            response.raise_for_status()
            
            # Processar resposta
            if response.content:
                result = response.json()
                
                # Verificar erros na resposta da API
                if 'error' in result and result['error']:
                    error_code = result.get('error', {}).get('code', 'unknown')
                    error_message = result.get('error', {}).get('message', 'Unknown error')
                    raise Exception(f"Erro na API do TikTok: {error_code} - {error_message}")
                
                # Salvar no cache se disponível
                if self.cache_manager and use_cache and method.upper() == 'GET':
                    self.cache_manager.set('tiktok', endpoint, params, result, 'default', cache_ttl)
                
                return result
            return {}
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Token expirado, tentar renovar
                self._refresh_access_token()
                # Tentar novamente com o novo token
                return self._make_request(method, endpoint, params, data, use_cache, cache_ttl)
            elif e.response.status_code == 429:
                # Rate limit atingido
                retry_after = int(e.response.headers.get('Retry-After', 60))
                time.sleep(retry_after)
                # Tentar novamente após espera
                return self._make_request(method, endpoint, params, data, use_cache, cache_ttl)
            else:
                # Outros erros HTTP
                try:
                    error_data = e.response.json() if e.response.content else {}
                    error_message = error_data.get('error', {}).get('message', str(e))
                except (ValueError, requests.exceptions.JSONDecodeError):
                    error_message = f"Erro HTTP {e.response.status_code}: {e.response.text[:200] if e.response.text else 'Resposta vazia'}"
                raise Exception(f"Erro na API do TikTok: {error_message} (Status: {e.response.status_code})")
        except requests.exceptions.RequestException as e:
            # Erros de conexão
            raise Exception(f"Erro de conexão com a API do TikTok: {str(e)}")
    
    def _refresh_access_token(self) -> None:
        """
        Renova o token de acesso.
        
        Raises:
            Exception: Erro ao renovar o token
        """
        try:
            response = requests.post(
                self.auth_url,
                data={
                    'client_key': self.client_key,
                    'client_secret': self.client_secret,
                    'grant_type': 'client_credentials'
                }
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            if 'data' in token_data and 'access_token' in token_data['data']:
                self.access_token = token_data['data']['access_token']
            else:
                raise Exception("Resposta inválida ao renovar token do TikTok")
                
        except Exception as e:
            raise Exception(f"Erro ao renovar token do TikTok: {str(e)}")
    
    def get_user_info(self, username: str) -> Dict:
        """
        Obtém informações de um usuário do TikTok pelo nome de usuário.
        
        Args:
            username: Nome de usuário do TikTok
            
        Returns:
            Dict: Dados do usuário
        """
        return self._make_request(
            'GET',
            'user/info/',
            params={'username': username}
        )
    
    def get_user_videos(self, user_id: str, cursor: str = None, max_count: int = 20) -> Dict:
        """
        Obtém os vídeos de um usuário do TikTok.
        
        Args:
            user_id: ID do usuário do TikTok
            cursor: Cursor para paginação
            max_count: Número máximo de vídeos a retornar
            
        Returns:
            Dict: Lista de vídeos
        """
        params = {
            'user_id': user_id,
            'max_count': max_count
        }
        
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request(
            'GET',
            'video/list/',
            params=params
        )
    
    def get_video_info(self, video_id: str) -> Dict:
        """
        Obtém informações detalhadas de um vídeo.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Dict: Dados do vídeo
        """
        return self._make_request(
            'GET',
            'video/info/',
            params={'video_id': video_id}
        )
    
    def get_video_comments(self, video_id: str, cursor: str = None, max_count: int = 50) -> Dict:
        """
        Obtém os comentários de um vídeo.
        
        Args:
            video_id: ID do vídeo
            cursor: Cursor para paginação
            max_count: Número máximo de comentários a retornar
            
        Returns:
            Dict: Lista de comentários
        """
        params = {
            'video_id': video_id,
            'max_count': max_count
        }
        
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request(
            'GET',
            'comment/list/',
            params=params
        )
    
    def search_videos(self, keyword: str, cursor: str = None, max_count: int = 20) -> Dict:
        """
        Pesquisa vídeos por palavra-chave.
        
        Args:
            keyword: Palavra-chave para pesquisa
            cursor: Cursor para paginação
            max_count: Número máximo de vídeos a retornar
            
        Returns:
            Dict: Resultados da pesquisa
        """
        params = {
            'keyword': keyword,
            'max_count': max_count
        }
        
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request(
            'GET',
            'search/video/',
            params=params
        )
    
    def get_trending_videos(self, cursor: str = None, max_count: int = 20) -> Dict:
        """
        Obtém os vídeos em tendência.
        
        Args:
            cursor: Cursor para paginação
            max_count: Número máximo de vídeos a retornar
            
        Returns:
            Dict: Lista de vídeos em tendência
        """
        params = {'max_count': max_count}
        
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request(
            'GET',
            'trending/video/',
            params=params
        )
    
    def get_hashtag_info(self, hashtag_name: str) -> Dict:
        """
        Obtém informações sobre uma hashtag.
        
        Args:
            hashtag_name: Nome da hashtag (sem o #)
            
        Returns:
            Dict: Informações da hashtag
        """
        return self._make_request(
            'GET',
            'hashtag/info/',
            params={'hashtag_name': hashtag_name}
        )
    
    def get_hashtag_videos(self, hashtag_id: str, cursor: str = None, max_count: int = 20) -> Dict:
        """
        Obtém vídeos de uma hashtag específica.
        
        Args:
            hashtag_id: ID da hashtag
            cursor: Cursor para paginação
            max_count: Número máximo de vídeos a retornar
            
        Returns:
            Dict: Lista de vídeos
        """
        params = {
            'hashtag_id': hashtag_id,
            'max_count': max_count
        }
        
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request(
            'GET',
            'hashtag/video/',
            params=params
        )
    
    def get_user_followers(self, user_id: str, cursor: str = None, max_count: int = 50) -> Dict:
        """
        Obtém os seguidores de um usuário.
        
        Args:
            user_id: ID do usuário
            cursor: Cursor para paginação
            max_count: Número máximo de seguidores a retornar
            
        Returns:
            Dict: Lista de seguidores
        """
        params = {
            'user_id': user_id,
            'max_count': max_count
        }
        
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request(
            'GET',
            'user/followers/',
            params=params
        )
    
    def get_user_following(self, user_id: str, cursor: str = None, max_count: int = 50) -> Dict:
        """
        Obtém os usuários que um usuário segue.
        
        Args:
            user_id: ID do usuário
            cursor: Cursor para paginação
            max_count: Número máximo de usuários a retornar
            
        Returns:
            Dict: Lista de usuários seguidos
        """
        params = {
            'user_id': user_id,
            'max_count': max_count
        }
        
        if cursor:
            params['cursor'] = cursor
        
        return self._make_request(
            'GET',
            'user/following/',
            params=params
        )