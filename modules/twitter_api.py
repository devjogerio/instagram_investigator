#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para interação com a API do Twitter/X
"""

import requests
import json
import time
import logging
import os
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Union
from modules.performance_optimizer import PerformanceOptimizer, rate_limit_decorator, CircuitBreaker

logger = logging.getLogger(__name__)

class TwitterAPI:
    """Classe para interação com a API do Twitter/X"""
    
    BASE_URL = "https://api.twitter.com/2"
    
    def __init__(self, bearer_token=None, cache_manager=None, performance_optimizer=None):
        """
        Inicializa a API do Twitter com as credenciais necessárias.
        
        Args:
            bearer_token: Token de autenticação da API do Twitter (opcional, pode vir do .env)
            cache_manager: Gerenciador de cache opcional para armazenar respostas
            performance_optimizer: Otimizador de performance opcional
        """
        load_dotenv()
        
        # Usa o token fornecido ou busca no ambiente
        if bearer_token:
            self.bearer_token = bearer_token
        else:
            self.bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
            
        self.api_key = os.getenv('TWITTER_API_KEY')
        self.api_secret = os.getenv('TWITTER_API_SECRET')
        self.access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        self.headers = {
            "Authorization": f"Bearer {self.bearer_token}",
            "Content-Type": "application/json"
        }
        
        self.rate_limit_remaining = 300  # Valor padrão, será atualizado com as respostas
        self.rate_limit_reset = 0
        
        self.cache_manager = cache_manager
        
        # Inicializa o otimizador de performance
        if performance_optimizer:
            self.performance_optimizer = performance_optimizer
        else:
            self.performance_optimizer = PerformanceOptimizer(
                max_retries=5,  # Twitter permite mais retries
                backoff_factor=0.2,
                timeout=30
            )
        
        # Configura circuit breaker para requisições
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=180,  # 3 minutos
            expected_exception=requests.exceptions.RequestException
        )
        
        self.session = self.performance_optimizer.session
    
    def _make_request(self, endpoint, params=None, max_retries=3, delay=2):
        """Realiza uma requisição à API do Twitter com tratamento de erros e rate limiting
        
        Args:
            endpoint: Endpoint da API a ser acessado
            params: Parâmetros da requisição
            max_retries: Número máximo de tentativas em caso de falha
            delay: Tempo de espera entre tentativas (em segundos)
            
        Returns:
            dict: Dados da resposta em formato JSON
            
        Raises:
            Exception: Em caso de falha após todas as tentativas
        """
        url = f"{self.BASE_URL}/{endpoint}"
        retries = 0
        
        while retries < max_retries:
            try:
                response = requests.get(url, headers=self.headers, params=params)
                
                # Verifica se a requisição foi bem-sucedida
                if response.status_code == 200:
                    return response.json()
                
                # Trata rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", delay))
                    logger.warning(f"Rate limit atingido. Aguardando {retry_after} segundos.")
                    time.sleep(retry_after)
                    retries += 1
                    continue
                
                # Trata outros erros
                error_message = f"Erro na API do Twitter: {response.status_code} - {response.text}"
                logger.error(error_message)
                
                # Aguarda antes de tentar novamente
                time.sleep(delay)
                retries += 1
                
            except Exception as e:
                logger.error(f"Erro ao acessar API do Twitter: {str(e)}")
                time.sleep(delay)
                retries += 1
        
        raise Exception(f"Falha ao acessar a API do Twitter após {max_retries} tentativas")
    
    def get_user_by_username(self, username):
        """Obtém informações de um usuário pelo nome de usuário
        
        Args:
            username: Nome de usuário do Twitter (sem @)
            
        Returns:
            dict: Dados do usuário
        """
        endpoint = "users/by/username/{username}"
        params = {
            "user.fields": "created_at,description,entities,id,location,name,pinned_tweet_id,profile_image_url,protected,public_metrics,url,verified,withheld"
        }
        
        return self._make_request(endpoint.format(username=username), params=params)
    
    def get_user_tweets(self, user_id, max_results=100):
        """Obtém tweets de um usuário pelo ID
        
        Args:
            user_id: ID do usuário no Twitter
            max_results: Número máximo de tweets a serem retornados (máx. 100)
            
        Returns:
            dict: Lista de tweets do usuário
        """
        endpoint = f"users/{user_id}/tweets"
        params = {
            "max_results": max_results,
            "tweet.fields": "created_at,public_metrics,text,entities",
            "expansions": "attachments.media_keys",
            "media.fields": "type,url"
        }
        
        return self._make_request(endpoint, params=params)
    
    def get_user_followers(self, user_id, max_results=100):
        """Obtém seguidores de um usuário pelo ID
        
        Args:
            user_id: ID do usuário no Twitter
            max_results: Número máximo de seguidores a serem retornados (máx. 100)
            
        Returns:
            dict: Lista de seguidores do usuário
        """
        endpoint = f"users/{user_id}/followers"
        params = {
            "max_results": max_results,
            "user.fields": "created_at,description,id,name,profile_image_url,public_metrics,username,verified"
        }
        
        return self._make_request(endpoint, params=params)
    
    def get_user_following(self, user_id, max_results=100):
        """Obtém usuários seguidos por um usuário pelo ID
        
        Args:
            user_id: ID do usuário no Twitter
            max_results: Número máximo de usuários a serem retornados (máx. 100)
            
        Returns:
            dict: Lista de usuários seguidos
        """
        endpoint = f"users/{user_id}/following"
        params = {
            "max_results": max_results,
            "user.fields": "created_at,description,id,name,profile_image_url,public_metrics,username,verified"
        }
        
        return self._make_request(endpoint, params=params)