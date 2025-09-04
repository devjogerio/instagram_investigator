import requests
import time
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Union
from modules.performance_optimizer import PerformanceOptimizer, rate_limit_decorator, CircuitBreaker

class LinkedInAPI:
    """
    Classe para interagir com a API do LinkedIn.
    Fornece métodos para autenticação e requisições à API do LinkedIn.
    """
    
    def __init__(self, cache_manager=None, performance_optimizer=None):
        """
        Inicializa a API do LinkedIn com as credenciais necessárias.
        
        Args:
            cache_manager: Gerenciador de cache opcional para armazenar respostas
            performance_optimizer: Otimizador de performance opcional
        """
        load_dotenv()
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.redirect_uri = os.getenv('LINKEDIN_REDIRECT_URI')
        self.access_token = os.getenv('LINKEDIN_ACCESS_TOKEN')
        self.refresh_token = os.getenv('LINKEDIN_REFRESH_TOKEN')
        
        self.base_url = 'https://api.linkedin.com/v2'
        self.auth_url = 'https://www.linkedin.com/oauth/v2'
        
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
                timeout=45
            )
        
        # Configura circuit breaker para requisições
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=180,  # 3 minutos
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
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
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
    
    @rate_limit_decorator(calls_per_minute=20)  # LinkedIn tem limites mais restritivos
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None, 
                     use_cache: bool = True, cache_ttl: int = 3600) -> Dict:
        """
        Realiza uma requisição à API do LinkedIn com tratamento de erros e cache otimizado.
        
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
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_auth_headers()
        
        # Verificar cache se disponível e solicitado
        if self.cache_manager and use_cache and method.upper() == 'GET':
            cached_data = self.cache_manager.get('linkedin', endpoint, params, 'default')
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
                timeout=45
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
                
                # Salvar no cache se disponível
                if self.cache_manager and use_cache and method.upper() == 'GET':
                    self.cache_manager.set('linkedin', endpoint, params, result, 'default', cache_ttl)
                
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
                error_data = e.response.json() if e.response.content else {}
                error_message = error_data.get('message', str(e))
                raise Exception(f"Erro na API do LinkedIn: {error_message} (Status: {e.response.status_code})")
        except requests.exceptions.RequestException as e:
            # Erros de conexão
            raise Exception(f"Erro de conexão com a API do LinkedIn: {str(e)}")
    
    def _refresh_access_token(self) -> None:
        """
        Renova o token de acesso usando o refresh token.
        
        Raises:
            Exception: Erro ao renovar o token
        """
        if not self.refresh_token:
            raise Exception("Refresh token não disponível. Autenticação manual necessária.")
        
        try:
            response = requests.post(
                f"{self.auth_url}/accessToken",
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': self.refresh_token,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret
                }
            )
            
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                self.refresh_token = token_data['refresh_token']
                
        except Exception as e:
            raise Exception(f"Erro ao renovar token do LinkedIn: {str(e)}")
    
    def get_profile(self, user_id: str = 'me') -> Dict:
        """
        Obtém informações do perfil do LinkedIn.
        
        Args:
            user_id: ID do usuário ou 'me' para o usuário autenticado
            
        Returns:
            Dict: Dados do perfil
        """
        fields = [
            'id', 'firstName', 'lastName', 'profilePicture(displayImage~:playableStreams)',
            'headline', 'summary', 'industryName', 'locationName', 'positions',
            'educations', 'skills', 'languages', 'certifications'
        ]
        
        return self._make_request(
            'GET',
            f'people/{user_id}',
            params={'projection': f"({','.join(fields)})"}
        )
    
    def get_connections(self, user_id: str = 'me', start: int = 0, count: int = 50) -> Dict:
        """
        Obtém as conexões do usuário.
        
        Args:
            user_id: ID do usuário ou 'me' para o usuário autenticado
            start: Índice inicial para paginação
            count: Número de conexões a retornar
            
        Returns:
            Dict: Lista de conexões
        """
        return self._make_request(
            'GET',
            f'people/{user_id}/connections',
            params={
                'start': start,
                'count': count,
                'projection': '(id,firstName,lastName,headline,profilePicture)'
            }
        )
    
    def get_posts(self, user_id: str = 'me', start: int = 0, count: int = 20) -> Dict:
        """
        Obtém as publicações do usuário.
        
        Args:
            user_id: ID do usuário ou 'me' para o usuário autenticado
            start: Índice inicial para paginação
            count: Número de publicações a retornar
            
        Returns:
            Dict: Lista de publicações
        """
        return self._make_request(
            'GET',
            f'people/{user_id}/posts',
            params={
                'start': start,
                'count': count
            }
        )
    
    def get_company(self, company_id: str) -> Dict:
        """
        Obtém informações de uma empresa.
        
        Args:
            company_id: ID da empresa
            
        Returns:
            Dict: Dados da empresa
        """
        fields = [
            'id', 'name', 'tagline', 'description', 'websiteUrl',
            'logoImage', 'locations', 'foundedOn', 'specialities',
            'followerCount', 'employeeCount'
        ]
        
        return self._make_request(
            'GET',
            f'organizations/{company_id}',
            params={'projection': f"({','.join(fields)})"}
        )
    
    def search_people(self, keywords: str, start: int = 0, count: int = 20) -> Dict:
        """
        Pesquisa pessoas no LinkedIn.
        
        Args:
            keywords: Termos de pesquisa
            start: Índice inicial para paginação
            count: Número de resultados a retornar
            
        Returns:
            Dict: Resultados da pesquisa
        """
        return self._make_request(
            'GET',
            'search/people',
            params={
                'keywords': keywords,
                'start': start,
                'count': count
            }
        )
    
    def search_companies(self, keywords: str, start: int = 0, count: int = 20) -> Dict:
        """
        Pesquisa empresas no LinkedIn.
        
        Args:
            keywords: Termos de pesquisa
            start: Índice inicial para paginação
            count: Número de resultados a retornar
            
        Returns:
            Dict: Resultados da pesquisa
        """
        return self._make_request(
            'GET',
            'search/organizations',
            params={
                'keywords': keywords,
                'start': start,
                'count': count
            }
        )
    
    def get_profile_by_vanity_name(self, vanity_name: str) -> Dict:
        """
        Obtém perfil pelo nome personalizado da URL.
        
        Args:
            vanity_name: Nome personalizado da URL do perfil
            
        Returns:
            Dict: Dados do perfil
        """
        # Primeiro pesquisa o perfil pelo nome
        search_results = self.search_people(vanity_name, count=5)
        
        # Verifica se encontrou algum resultado
        if 'elements' in search_results and search_results['elements']:
            for profile in search_results['elements']:
                # Verifica se o vanity name corresponde
                if 'vanityName' in profile and profile['vanityName'].lower() == vanity_name.lower():
                    return self.get_profile(profile['id'])
        
        raise Exception(f"Perfil não encontrado para o vanity name: {vanity_name}")