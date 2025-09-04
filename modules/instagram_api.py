#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para comunicação com a API do Instagram
"""

import requests
import json
import time
from urllib.parse import quote_plus
import logging
import os
from dotenv import load_dotenv

# Importa o gerenciador de cache e otimizador de performance
from modules.cache_manager import CacheManager
from modules.performance_optimizer import PerformanceOptimizer, rate_limit_decorator, CircuitBreaker

logger = logging.getLogger(__name__)

# Carrega variáveis de ambiente
load_dotenv()


class InstagramAPI:
    """Classe para interação com a API do Instagram com otimizações de performance"""
    
    def __init__(self, session_id, cache_manager=None, performance_optimizer=None):
        """Inicializa a API com o session ID fornecido"""
        self.session_id = session_id
        self.headers = {"User-Agent": "Instagram 64.0.0.14.96"}
        self.api_headers = {"User-Agent": "iphone_ua", "x-ig-app-id": "936619743392459"}
        
        # Inicializa o gerenciador de cache
        if cache_manager:
            self.cache_manager = cache_manager
            self.cache = cache_manager  # Para compatibilidade com código existente
        else:
            cache_duration = int(os.getenv('CACHE_DURATION', 3600))  # Padrão: 1 hora
            self.cache = CacheManager(cache_dir="cache", cache_duration=cache_duration)
            self.cache_manager = self.cache
        
        # Inicializa o otimizador de performance
        if performance_optimizer:
            self.performance_optimizer = performance_optimizer
        else:
            self.performance_optimizer = PerformanceOptimizer(
                max_retries=3,
                backoff_factor=0.3,
                timeout=30
            )
        
        # Configura circuit breaker para requisições
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=300,  # 5 minutos
            expected_exception=requests.exceptions.RequestException
        )
    
    def get_user_id(self, username):
        """Obtém ID do usuário a partir do username"""
        endpoint = "user_id"
        params = {"username": username}
        
        # Verifica cache primeiro
        cached_data = self.cache.get(endpoint, params)
        if cached_data:
            logger.info(f"ID do usuário {username} recuperado do cache")
            return cached_data
        
        url = f'https://i.instagram.com/api/v1/users/web_profile_info/?username={username}'
        
        try:
            response = requests.get(
                url, 
                headers=self.api_headers, 
                cookies={'sessionid': self.session_id}, 
                timeout=30
            )
            
            if response.status_code == 404:
                logger.error(f"Usuário {username} não encontrado")
                return {"id": None, "error": "Usuário não encontrado"}
            
            if response.status_code == 429:
                logger.error("Rate limit atingido")
                return {"id": None, "error": "Rate limit atingido"}
            
            response.raise_for_status()
            data = response.json()
            user_id = data["data"]["user"]["id"]
            
            result = {"id": user_id, "error": None}
            
            # Salva no cache
            self.cache.set(endpoint, params, result)
            logger.info(f"ID do usuário {username} salvo no cache")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de rede: {str(e)}")
            return {"id": None, "error": f"Erro de rede: {str(e)}"}
        except json.JSONDecodeError:
            logger.error("Rate limit atingido ou resposta inválida")
            return {"id": None, "error": "Rate limit atingido ou resposta inválida"}
        except KeyError:
            logger.error("Formato de resposta inválido")
            return {"id": None, "error": "Formato de resposta inválido"}
    
    def get_user_info(self, user_id):
        """Obtém informações detalhadas do usuário"""
        endpoint = "user_info"
        params = {"user_id": user_id}
        
        # Verifica se os dados estão em cache
        cached_data = self.cache.get(endpoint, params)
        if cached_data:
            logger.info(f"Usando dados em cache para user_id {user_id}")
            return cached_data
        
        url = f'https://i.instagram.com/api/v1/users/{user_id}/info/'
        
        try:
            response = requests.get(
                url, 
                headers=self.headers, 
                cookies={'sessionid': self.session_id}, 
                timeout=30
            )
            
            if response.status_code == 429:
                logger.error("Rate limit atingido")
                return {"user": None, "error": "Rate limit atingido"}
            
            response.raise_for_status()
            data = response.json()
            
            user_info = data.get("user")
            if not user_info:
                logger.error("Usuário não encontrado")
                return {"user": None, "error": "Usuário não encontrado"}
            
            user_info["userID"] = user_id
            result = {"user": user_info, "error": None}
            
            # Armazena o resultado em cache
            self.cache.set(endpoint, params, result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de rede: {str(e)}")
            return {"user": None, "error": f"Erro de rede: {str(e)}"}
        except json.JSONDecodeError:
            logger.error("Resposta inválida")
            return {"user": None, "error": "Resposta inválida"}
    
    def advanced_lookup(self, username):
        """Realiza lookup avançado para informações ofuscadas"""
        endpoint = "advanced_lookup"
        params = {"username": username}
        
        # Verifica se os dados estão em cache
        cached_data = self.cache.get(endpoint, params)
        if cached_data:
            logger.info(f"Usando dados em cache para lookup avançado de {username}")
            return cached_data
        
        data_payload = "signed_body=SIGNATURE." + quote_plus(json.dumps(
            {"q": username, "skip_recovery": "1"}, separators=(",", ":")
        ))
        
        headers = {
            "Accept-Language": "en-US",
            "User-Agent": "Instagram 101.0.0.15.120",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-IG-App-ID": "124024574287414",
            "Accept-Encoding": "gzip, deflate",
            "Host": "i.instagram.com",
            "Connection": "keep-alive",
            "Content-Length": str(len(data_payload))
        }
        
        try:
            response = requests.post(
                'https://i.instagram.com/api/v1/users/lookup/',
                headers=headers, 
                data=data_payload, 
                timeout=30
            )
            
            if response.status_code == 429:
                logger.warning("Rate limit atingido no lookup avançado")
                return {"user": None, "error": "Rate limit"}
            
            response.raise_for_status()
            data = response.json()
            result = {"user": data, "error": None}
            
            # Armazena o resultado em cache
            self.cache.set(endpoint, params, result)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de rede: {str(e)}")
            return {"user": None, "error": f"Erro de rede: {str(e)}"}
        except json.JSONDecodeError:
            logger.error("Rate limit ou resposta inválida")
            return {"user": None, "error": "Rate limit"}