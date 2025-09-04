#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classe base para extratores de dados de redes sociais
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime

class BaseExtractor(ABC):
    """Classe base abstrata para extratores de dados de redes sociais."""
    
    def __init__(self, platform_name: str):
        """Inicializa o extrator base.
        
        Args:
            platform_name: Nome da plataforma (facebook, instagram, twitter, etc.)
        """
        self.platform_name = platform_name
        self.logger = logging.getLogger(f"{platform_name.title()}Extractor")
        self.extraction_timestamp = None
    
    @abstractmethod
    def extract_profile(self, username: str) -> Dict[str, Any]:
        """Extrai informações do perfil.
        
        Args:
            username: Nome de usuário da plataforma
            
        Returns:
            Dict: Dados do perfil extraídos
        """
        pass
    
    @abstractmethod
    def extract_posts(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Extrai posts do perfil.
        
        Args:
            username: Nome de usuário da plataforma
            limit: Número máximo de posts a serem extraídos
            
        Returns:
            List[Dict]: Lista de posts extraídos
        """
        pass
    
    def validate_username(self, username: str) -> bool:
        """Valida o formato do nome de usuário.
        
        Args:
            username: Nome de usuário a ser validado
            
        Returns:
            bool: True se válido, False caso contrário
        """
        if not username or not isinstance(username, str):
            return False
        
        # Remove @ se presente
        username = username.lstrip('@')
        
        # Verifica se não está vazio após remoção
        if not username:
            return False
        
        # Verifica caracteres básicos (pode ser sobrescrito por subclasses)
        return username.replace('_', '').replace('.', '').isalnum()
    
    def log_extraction_start(self, username: str, operation: str = "extraction"):
        """Registra o início de uma operação de extração.
        
        Args:
            username: Nome de usuário sendo processado
            operation: Tipo de operação sendo realizada
        """
        self.extraction_timestamp = datetime.now()
        self.logger.info(f"Iniciando {operation} para {self.platform_name}: {username}")
    
    def log_extraction_end(self, username: str, success: bool = True, operation: str = "extraction"):
        """Registra o fim de uma operação de extração.
        
        Args:
            username: Nome de usuário processado
            success: Se a operação foi bem-sucedida
            operation: Tipo de operação realizada
        """
        if self.extraction_timestamp:
            duration = (datetime.now() - self.extraction_timestamp).total_seconds()
            status = "concluída" if success else "falhou"
            self.logger.info(f"Operação {operation} para {self.platform_name}:{username} {status} em {duration:.2f}s")
    
    def format_standard_profile(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Formata dados do perfil em um formato padrão.
        
        Args:
            raw_data: Dados brutos do perfil
            
        Returns:
            Dict: Dados formatados no padrão comum
        """
        return {
            "platform": self.platform_name,
            "username": raw_data.get("username", ""),
            "display_name": raw_data.get("display_name", raw_data.get("name", "")),
            "user_id": raw_data.get("id", raw_data.get("user_id", "")),
            "bio": raw_data.get("bio", raw_data.get("description", "")),
            "profile_picture": raw_data.get("profile_picture", raw_data.get("avatar", "")),
            "followers_count": raw_data.get("followers_count", 0),
            "following_count": raw_data.get("following_count", 0),
            "posts_count": raw_data.get("posts_count", raw_data.get("media_count", 0)),
            "is_verified": raw_data.get("is_verified", False),
            "is_private": raw_data.get("is_private", False),
            "external_url": raw_data.get("external_url", raw_data.get("website", "")),
            "location": raw_data.get("location", ""),
            "created_at": raw_data.get("created_at", ""),
            "extraction_timestamp": datetime.now().isoformat(),
            "raw_data": raw_data  # Mantém dados originais para referência
        }
    
    def format_standard_post(self, raw_post: Dict[str, Any]) -> Dict[str, Any]:
        """Formata dados do post em um formato padrão.
        
        Args:
            raw_post: Dados brutos do post
            
        Returns:
            Dict: Dados formatados no padrão comum
        """
        return {
            "platform": self.platform_name,
            "post_id": raw_post.get("id", raw_post.get("post_id", "")),
            "content": raw_post.get("content", raw_post.get("caption", raw_post.get("text", ""))),
            "created_at": raw_post.get("created_at", raw_post.get("timestamp", "")),
            "media_type": raw_post.get("media_type", "text"),
            "media_url": raw_post.get("media_url", ""),
            "likes_count": raw_post.get("likes_count", raw_post.get("like_count", 0)),
            "comments_count": raw_post.get("comments_count", raw_post.get("comment_count", 0)),
            "shares_count": raw_post.get("shares_count", raw_post.get("share_count", 0)),
            "views_count": raw_post.get("views_count", raw_post.get("view_count", 0)),
            "hashtags": raw_post.get("hashtags", []),
            "mentions": raw_post.get("mentions", []),
            "url": raw_post.get("url", raw_post.get("permalink", "")),
            "raw_data": raw_post  # Mantém dados originais para referência
        }
    
    def handle_rate_limit(self, wait_time: int = 60):
        """Lida com limite de taxa da API.
        
        Args:
            wait_time: Tempo de espera em segundos
        """
        self.logger.warning(f"Limite de taxa atingido. Aguardando {wait_time} segundos...")
        import time
        time.sleep(wait_time)
    
    def handle_error(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Lida com erros de extração de forma padronizada.
        
        Args:
            error: Exceção ocorrida
            context: Contexto adicional do erro
            
        Returns:
            Dict: Dados de erro formatados
        """
        error_msg = f"Erro na extração {self.platform_name}"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {str(error)}"
        
        self.logger.error(error_msg)
        
        return {
            "success": False,
            "platform": self.platform_name,
            "error": str(error),
            "error_context": context,
            "timestamp": datetime.now().isoformat()
        }