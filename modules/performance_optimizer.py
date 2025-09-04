#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de otimização de performance para APIs de redes sociais
Implementa connection pooling, retry logic e timeouts configuráveis
"""

import time
import random
import logging
import requests
from typing import Dict, Any, Optional, Callable
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from functools import wraps

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """
    Classe para otimização de performance de requisições HTTP
    """
    
    def __init__(self, 
                 max_retries: int = 3,
                 backoff_factor: float = 0.3,
                 timeout: int = 30,
                 pool_connections: int = 10,
                 pool_maxsize: int = 20):
        """
        Inicializa o otimizador de performance
        
        Args:
            max_retries: Número máximo de tentativas
            backoff_factor: Fator de backoff exponencial
            timeout: Timeout padrão para requisições
            pool_connections: Número de pools de conexão
            pool_maxsize: Tamanho máximo do pool
        """
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        
        # Configura session com connection pooling
        self.session = requests.Session()
        
        # Configura retry strategy
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=backoff_factor
        )
        
        # Configura adapter com connection pooling
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def exponential_backoff(self, attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """
        Calcula delay com backoff exponencial e jitter
        
        Args:
            attempt: Número da tentativa atual
            base_delay: Delay base em segundos
            max_delay: Delay máximo em segundos
            
        Returns:
            float: Tempo de espera em segundos
        """
        delay = min(base_delay * (2 ** attempt), max_delay)
        # Adiciona jitter para evitar thundering herd
        jitter = random.uniform(0.1, 0.3) * delay
        return delay + jitter
    
    def retry_with_backoff(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa função com retry e backoff exponencial
        
        Args:
            func: Função a ser executada
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Any: Resultado da função
            
        Raises:
            Exception: Após esgotar todas as tentativas
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)
            except (requests.exceptions.RequestException, 
                    requests.exceptions.Timeout,
                    requests.exceptions.ConnectionError) as e:
                last_exception = e
                
                if attempt < self.max_retries:
                    delay = self.exponential_backoff(attempt)
                    logger.warning(f"Tentativa {attempt + 1} falhou: {str(e)}. Tentando novamente em {delay:.2f}s")
                    time.sleep(delay)
                else:
                    logger.error(f"Todas as {self.max_retries + 1} tentativas falharam")
                    break
            except Exception as e:
                # Para outros tipos de exceção, não tenta novamente
                logger.error(f"Erro não recuperável: {str(e)}")
                raise e
        
        raise last_exception
    
    def make_optimized_request(self, 
                             method: str, 
                             url: str, 
                             timeout: Optional[int] = None,
                             **kwargs) -> requests.Response:
        """
        Faz requisição otimizada com retry e connection pooling
        
        Args:
            method: Método HTTP
            url: URL da requisição
            timeout: Timeout específico (usa padrão se None)
            **kwargs: Argumentos adicionais para requests
            
        Returns:
            requests.Response: Resposta da requisição
        """
        timeout = timeout or self.timeout
        
        def _make_request():
            return self.session.request(
                method=method,
                url=url,
                timeout=timeout,
                **kwargs
            )
        
        return self.retry_with_backoff(_make_request)
    
    def close(self):
        """Fecha a sessão e libera recursos"""
        if self.session:
            self.session.close()


def rate_limit_decorator(calls_per_minute: int = 60):
    """
    Decorator para controle de rate limiting
    
    Args:
        calls_per_minute: Número máximo de chamadas por minuto
    """
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            time_since_last = current_time - last_called[0]
            
            if time_since_last < min_interval:
                sleep_time = min_interval - time_since_last
                logger.debug(f"Rate limiting: aguardando {sleep_time:.2f}s")
                time.sleep(sleep_time)
            
            last_called[0] = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def timeout_decorator(timeout_seconds: int = 30):
    """
    Decorator para timeout de funções
    
    Args:
        timeout_seconds: Timeout em segundos
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"Função {func.__name__} excedeu timeout de {timeout_seconds}s")
            
            # Configura o timeout (apenas em sistemas Unix)
            try:
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(timeout_seconds)
                
                result = func(*args, **kwargs)
                
                signal.alarm(0)  # Cancela o timeout
                return result
            except AttributeError:
                # Windows não suporta SIGALRM, executa sem timeout
                logger.warning("Timeout não suportado neste sistema")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


class CircuitBreaker:
    """
    Implementa padrão Circuit Breaker para APIs
    """
    
    def __init__(self, 
                 failure_threshold: int = 5,
                 recovery_timeout: int = 60,
                 expected_exception: type = Exception):
        """
        Inicializa o Circuit Breaker
        
        Args:
            failure_threshold: Número de falhas antes de abrir o circuito
            recovery_timeout: Tempo para tentar fechar o circuito novamente
            expected_exception: Tipo de exceção esperada
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == 'OPEN':
                if self._should_attempt_reset():
                    self.state = 'HALF_OPEN'
                else:
                    raise Exception("Circuit breaker está OPEN")
            
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e
        
        return wrapper
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuit breaker"""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Chamado quando a operação é bem-sucedida"""
        self.failure_count = 0
        self.state = 'CLOSED'
    
    def _on_failure(self):
        """Chamado quando a operação falha"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'OPEN'
            logger.warning(f"Circuit breaker OPEN após {self.failure_count} falhas")