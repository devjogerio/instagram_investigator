#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para interação com a API do Facebook
"""

import time
import logging
import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Union
from modules.performance_optimizer import PerformanceOptimizer, rate_limit_decorator, CircuitBreaker

logger = logging.getLogger(__name__)

class FacebookAPI:
    """Classe para interação com a API do Facebook"""
    
    BASE_URL = "https://graph.facebook.com/v18.0"
    
    def __init__(self, app_id=None, app_secret=None, access_token=None, cache_manager=None, performance_optimizer=None):
        """Inicializa a API do Facebook
        
        Args:
            app_id: ID do aplicativo Facebook (opcional, pode vir do .env)
            app_secret: Chave secreta do aplicativo Facebook (opcional, pode vir do .env)
            access_token: Token de acesso para a API do Facebook (opcional, pode vir do .env)
            cache_manager: Gerenciador de cache opcional para armazenar respostas
            performance_optimizer: Otimizador de performance opcional
        """
        load_dotenv()
        
        self.app_id = app_id or os.getenv('FACEBOOK_APP_ID')
        self.app_secret = app_secret or os.getenv('FACEBOOK_APP_SECRET')
        self.access_token = access_token or os.getenv('FACEBOOK_ACCESS_TOKEN')
        
        self.rate_limit_remaining = 200  # Valor padrão
        self.rate_limit_reset = datetime.now() + timedelta(hours=1)
        
        self.cache_manager = cache_manager
        
        # Inicializa o otimizador de performance
        if performance_optimizer:
            self.performance_optimizer = performance_optimizer
        else:
            self.performance_optimizer = PerformanceOptimizer(
                max_retries=3,
                backoff_factor=0.3,
                timeout=60  # Facebook pode ser mais lento
            )
        
        # Configura circuit breaker para requisições
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,  # Facebook é mais tolerante
            recovery_timeout=300,  # 5 minutos
            expected_exception=requests.exceptions.RequestException
        )
        
        self.session = self.performance_optimizer.session
    
    def _make_request(self, endpoint, params=None, method="GET"):
        """Realiza uma requisição para a API do Facebook
        
        Args:
            endpoint: Endpoint da API
            params: Parâmetros da requisição
            method: Método HTTP (GET, POST, etc)
            
        Returns:
            dict: Resposta da API
            
        Raises:
            Exception: Em caso de erro na requisição
        """
        if params is None:
            params = {}
            
        # Adiciona token de acesso aos parâmetros
        params["access_token"] = self.access_token
        
        # Verifica limite de taxa
        if self.rate_limit_remaining <= 0:
            wait_time = (self.rate_limit_reset - datetime.now()).total_seconds()
            if wait_time > 0:
                logger.warning(f"Limite de taxa atingido. Aguardando {wait_time:.1f} segundos.")
                time.sleep(wait_time)
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            # Verifica cache primeiro
            cache_key = f"facebook_{endpoint}_{hash(str(params))}"
            if self.cache_manager and method == "GET":
                cached_response = self.cache_manager.get(cache_key)
                if cached_response:
                    logger.info(f"Cache hit para endpoint: {endpoint}")
                    return cached_response
            
            # Usa circuit breaker para a requisição
            if method == "GET":
                response = self.circuit_breaker.call(self.session.get, url, params=params)
            elif method == "POST":
                response = self.circuit_breaker.call(self.session.post, url, data=params)
            else:
                raise ValueError(f"Método HTTP não suportado: {method}")
                
            # Atualiza informações de limite de taxa
            if "x-app-usage" in response.headers:
                usage = response.headers.get("x-app-usage")
                if usage and isinstance(usage, dict):
                    self.rate_limit_remaining = 200 - usage.get("call_count", 0)
                    self.rate_limit_reset = datetime.now() + timedelta(hours=1)
            
            # Verifica se a resposta foi bem-sucedida
            if response.status_code == 200:
                result = response.json()
                
                # Armazena no cache se disponível
                if self.cache_manager and method == "GET":
                    self.cache_manager.set(cache_key, result, ttl=3600)  # Cache por 1 hora
                
                return result
            else:
                error_data = response.json() if response.content else {"message": "Erro desconhecido"}
                error_message = error_data.get("error", {}).get("message", "Erro desconhecido")
                error_code = error_data.get("error", {}).get("code", 0)
                
                logger.error(f"Erro na API do Facebook: {error_message} (Código: {error_code})")
                raise Exception(f"Erro na API do Facebook: {error_message} (Código: {error_code})")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexão com a API do Facebook: {str(e)}")
            raise Exception(f"Erro de conexão com a API do Facebook: {str(e)}")
    
    @rate_limit_decorator(calls_per_minute=100)
    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Obtém informações do perfil de um usuário
        
        Args:
            user_id: ID ou nome de usuário do Facebook
            
        Returns:
            dict: Dados do perfil do usuário
        """
        fields = "id,name,picture,link,about,birthday,email,gender,hometown,location,website"
        
        return self._make_request(
            endpoint=user_id,
            params={"fields": fields}
        )
    
    @rate_limit_decorator(calls_per_minute=100)
    def get_user_posts(self, user_id: str, limit: int = 100) -> Dict[str, Any]:
        """Obtém posts de um usuário
        
        Args:
            user_id: ID ou nome de usuário do Facebook
            limit: Número máximo de posts a retornar
            
        Returns:
            dict: Dados dos posts do usuário
        """
        fields = "id,message,created_time,permalink_url,full_picture,type,shares,reactions.summary(true),comments.summary(true)"
        
        return self._make_request(
            endpoint=f"{user_id}/posts",
            params={"fields": fields, "limit": limit}
        )
    
    def get_user_photos(self, user_id, limit=100):
        """Obtém fotos de um usuário
        
        Args:
            user_id: ID ou nome de usuário do Facebook
            limit: Número máximo de fotos a retornar
            
        Returns:
            dict: Dados das fotos do usuário
        """
        fields = "id,album,created_time,images,name,place,reactions.summary(true),comments.summary(true)"
        
        return self._make_request(
            endpoint=f"{user_id}/photos",
            params={"fields": fields, "limit": limit}
        )
    
    def get_user_videos(self, user_id, limit=100):
        """Obtém vídeos de um usuário
        
        Args:
            user_id: ID ou nome de usuário do Facebook
            limit: Número máximo de vídeos a retornar
            
        Returns:
            dict: Dados dos vídeos do usuário
        """
        fields = "id,description,created_time,permalink_url,title,reactions.summary(true),comments.summary(true)"
        
        return self._make_request(
            endpoint=f"{user_id}/videos",
            params={"fields": fields, "limit": limit}
        )
    
    def get_user_events(self, user_id, limit=100):
        """Obtém eventos de um usuário
        
        Args:
            user_id: ID ou nome de usuário do Facebook
            limit: Número máximo de eventos a retornar
            
        Returns:
            dict: Dados dos eventos do usuário
        """
        fields = "id,name,description,start_time,end_time,place,attending_count,interested_count"
        
        return self._make_request(
            endpoint=f"{user_id}/events",
            params={"fields": fields, "limit": limit}
        )
    
    def get_user_friends(self, user_id, limit=100):
        """Obtém amigos de um usuário
        
        Args:
            user_id: ID ou nome de usuário do Facebook
            limit: Número máximo de amigos a retornar
            
        Returns:
            dict: Dados dos amigos do usuário
        """
        fields = "id,name,picture"
        
        return self._make_request(
            endpoint=f"{user_id}/friends",
            params={"fields": fields, "limit": limit}
        )
    
    def get_page_info(self, page_id):
        """Obtém informações de uma página
        
        Args:
            page_id: ID ou nome da página do Facebook
            
        Returns:
            dict: Dados da página
        """
        fields = "id,name,about,category,fan_count,link,location,phone,website,picture"
        
        return self._make_request(
            endpoint=page_id,
            params={"fields": fields}
        )
    
    def get_page_posts(self, page_id, limit=100):
        """Obtém posts de uma página
        
        Args:
            page_id: ID ou nome da página do Facebook
            limit: Número máximo de posts a retornar
            
        Returns:
            dict: Dados dos posts da página
        """
        fields = "id,message,created_time,permalink_url,full_picture,type,shares,reactions.summary(true),comments.summary(true)"
        
        return self._make_request(
            endpoint=f"{page_id}/posts",
            params={"fields": fields, "limit": limit}
        )
    
    def search_users(self, query, limit=25):
        """Pesquisa usuários pelo nome
        
        Args:
            query: Termo de pesquisa
            limit: Número máximo de resultados a retornar
            
        Returns:
            dict: Resultados da pesquisa
        """
        return self._make_request(
            endpoint="search",
            params={"q": query, "type": "user", "limit": limit}
        )
    
    def search_pages(self, query, limit=25):
        """Pesquisa páginas pelo nome
        
        Args:
            query: Termo de pesquisa
            limit: Número máximo de resultados a retornar
            
        Returns:
            dict: Resultados da pesquisa
        """
        return self._make_request(
            endpoint="search",
            params={"q": query, "type": "page", "limit": limit}
        )
    
    def search_events(self, query, limit=25):
        """Pesquisa eventos pelo nome
        
        Args:
            query: Termo de pesquisa
            limit: Número máximo de resultados a retornar
            
        Returns:
            dict: Resultados da pesquisa
        """
        return self._make_request(
            endpoint="search",
            params={"q": query, "type": "event", "limit": limit}
        )