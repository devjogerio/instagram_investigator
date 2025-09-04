import os
import re
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

from modules.base_extractor import BaseExtractor
from modules.facebook_api import FacebookAPI

class FacebookExtractor(BaseExtractor):
    """Extrator de dados do Facebook."""
    
    def __init__(self, app_id: str = None, app_secret: str = None, access_token: str = None):
        """Inicializa o extrator do Facebook.
        
        Args:
            app_id: ID do aplicativo Facebook
            app_secret: Chave secreta do aplicativo Facebook
            access_token: Token de acesso para a API do Facebook
        """
        super().__init__("facebook")
        
        # Inicializa a API do Facebook com as credenciais fornecidas
        if app_id and app_secret and access_token:
            self.api_client = FacebookAPI(app_id, app_secret, access_token)
        else:
            # Tenta obter credenciais das variáveis de ambiente
            import os
            app_id = os.getenv('FACEBOOK_APP_ID')
            app_secret = os.getenv('FACEBOOK_APP_SECRET')
            access_token = os.getenv('FACEBOOK_ACCESS_TOKEN')
            
            if app_id and app_secret and access_token:
                self.api_client = FacebookAPI(app_id, app_secret, access_token)
            else:
                self.logger.warning("Credenciais do Facebook não fornecidas. Algumas funcionalidades podem não funcionar.")
                self.api_client = None
    
    def extract_profile(self, username: str) -> Dict[str, Any]:
        """Extrai informações do perfil do Facebook.
        
        Args:
            username: Nome de usuário do Facebook
            
        Returns:
            Dict: Dados do perfil
        """
        self.logger.info(f"Extraindo perfil do Facebook: {username}")
        
        try:
            if not self.api_client:
                return self.handle_error(Exception("API do Facebook não configurada"), "extract_profile")
            
            self.log_extraction_start(username, "extração de perfil")
            
            # Obtém dados do perfil via API
            profile_data = self.api_client.get_user_profile(username)
            
            if not profile_data:
                self.logger.warning(f"Nenhum dado encontrado para o perfil: {username}")
                return self.handle_error(Exception("Perfil não encontrado"), "extract_profile")
            
            # Formata os dados do perfil usando o método da classe base
            formatted_profile = self.format_standard_profile(profile_data)
            
            # Adiciona dados específicos do Facebook
            formatted_profile.update(self._format_facebook_specific_data(profile_data))
            
            # Adiciona posts ao perfil
            posts = self.extract_posts(username)
            formatted_profile["posts"] = posts
            
            self.log_extraction_end(username, True, "extração de perfil")
            return formatted_profile
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair perfil do Facebook: {str(e)}")
            return {}
    
    def extract_posts(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Extrai posts do perfil do Facebook.
        
        Args:
            username: Nome de usuário do Facebook
            limit: Número máximo de posts a serem extraídos
            
        Returns:
            List[Dict]: Lista de posts
        """
        self.logger.info(f"Extraindo posts do Facebook para: {username} (limite: {limit})")
        
        try:
            if not self.api_client:
                self.logger.error("API do Facebook não configurada")
                return []
            
            self.log_extraction_start(username, "extração de posts")
            
            # Primeiro obtém o perfil para ter o user_id
            profile_data = self.api_client.get_user_profile(username)
            if not profile_data or 'id' not in profile_data:
                self.logger.warning(f"Não foi possível obter ID do usuário: {username}")
                return []
            
            user_id = profile_data['id']
            
            # Obtém posts via API
            posts_response = self.api_client.get_user_posts(user_id, limit)
            
            if not posts_response or 'data' not in posts_response:
                self.logger.warning(f"Nenhum post encontrado para: {username}")
                return []
            
            posts_data = posts_response['data']
            
            # Formata os dados dos posts usando o método da classe base
            formatted_posts = [self.format_standard_post(post) for post in posts_data]
            
            self.log_extraction_end(username, True, "extração de posts")
            return formatted_posts
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair posts do Facebook: {str(e)}")
            return []
    
    def extract_connections(self, username: str) -> Dict[str, Any]:
        """Extrai conexões do perfil do Facebook.
        
        Args:
            username: Nome de usuário do Facebook
            
        Returns:
            Dict: Dados de conexões
        """
        self.logger.info(f"Extraindo conexões do Facebook para: {username}")
        
        try:
            if not self.api_client:
                self.logger.error("API do Facebook não configurada")
                return {}
            
            self.log_extraction_start(username, "extração de conexões")
            
            # Primeiro obtém o perfil para ter o user_id
            profile_data = self.api_client.get_user_profile(username)
            if not profile_data or 'id' not in profile_data:
                self.logger.warning(f"Não foi possível obter ID do usuário: {username}")
                return {}
            
            user_id = profile_data['id']
            
            # Obtém dados de amigos via API
            friends_data = self.api_client.get_user_friends(user_id)
            
            # Formata os dados de conexões
            formatted_connections = {
                "friends_count": len(friends_data.get("data", [])) if friends_data else 0,
                "friends_sample": friends_data.get("data", [])[:10] if friends_data else [],  # Primeiros 10 amigos
                "extraction_timestamp": datetime.now().isoformat()
            }
            
            self.log_extraction_end(username, True, "extração de conexões")
            return formatted_connections
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair conexões do Facebook: {str(e)}")
            return {}
    
    def extract_engagement(self, username: str) -> Dict[str, Any]:
        """Extrai métricas de engajamento do perfil do Facebook.
        
        Args:
            username: Nome de usuário do Facebook
            
        Returns:
            Dict: Dados de engajamento
        """
        self.logger.info(f"Extraindo engajamento do Facebook para: {username}")
        
        try:
            # Obtém posts para calcular engajamento
            posts = self.extract_posts(username, limit=50)
            
            if not posts:
                self.logger.warning(f"Nenhum post encontrado para calcular engajamento: {username}")
                return {}
            
            # Calcula métricas de engajamento
            total_likes = sum(post.get("likes_count", 0) for post in posts)
            total_comments = sum(post.get("comments_count", 0) for post in posts)
            total_shares = sum(post.get("shares_count", 0) for post in posts)
            post_count = len(posts)
            
            # Calcula médias
            avg_likes = total_likes / post_count if post_count > 0 else 0
            avg_comments = total_comments / post_count if post_count > 0 else 0
            avg_shares = total_shares / post_count if post_count > 0 else 0
            
            # Calcula engajamento total
            total_engagement = total_likes + total_comments + total_shares
            avg_engagement = total_engagement / post_count if post_count > 0 else 0
            
            # Formata os dados de engajamento
            engagement_data = {
                "total_posts": post_count,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "total_shares": total_shares,
                "total_engagement": total_engagement,
                "avg_likes_per_post": avg_likes,
                "avg_comments_per_post": avg_comments,
                "avg_shares_per_post": avg_shares,
                "avg_engagement_per_post": avg_engagement,
                "extraction_timestamp": datetime.now().isoformat()
            }
            
            return engagement_data
            
        except Exception as e:
            self.logger.error(f"Erro ao extrair engajamento do Facebook: {str(e)}")
            return {}
    
    def _format_facebook_specific_data(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Formata dados específicos do Facebook que não estão no formato padrão.
        
        Args:
            profile_data: Dados brutos do perfil do Facebook
            
        Returns:
            Dict: Dados específicos do Facebook formatados
        """
        return {
            "facebook_id": profile_data.get("id", ""),
            "about": profile_data.get("about", ""),
            "birthday": profile_data.get("birthday", ""),
            "email": profile_data.get("email", ""),
            "gender": profile_data.get("gender", ""),
            "hometown": profile_data.get("hometown", {}).get("name", "") if isinstance(profile_data.get("hometown"), dict) else profile_data.get("hometown", ""),
            "category": profile_data.get("category", ""),
            "link": profile_data.get("link", ""),
            "locale": profile_data.get("locale", ""),
            "timezone": profile_data.get("timezone", ""),
            "updated_time": profile_data.get("updated_time", ""),
            "cover_photo": profile_data.get("cover", {}).get("source", "") if isinstance(profile_data.get("cover"), dict) else ""
        }
    
    def format_standard_post(self, raw_post: Dict[str, Any]) -> Dict[str, Any]:
        """Sobrescreve o método da classe base para formatação específica do Facebook.
        
        Args:
            raw_post: Dados brutos do post do Facebook
            
        Returns:
            Dict: Dados formatados no padrão comum com especificidades do Facebook
        """
        # Usa o método da classe base como base
        formatted_post = super().format_standard_post(raw_post)
        
        # Adiciona campos específicos do Facebook
        formatted_post.update({
            "content": raw_post.get("message", ""),
            "media_type": self._determine_media_type(raw_post),
            "media_url": self._extract_media_url(raw_post),
            "likes_count": raw_post.get("reactions", {}).get("summary", {}).get("total_count", 0),
            "comments_count": raw_post.get("comments", {}).get("summary", {}).get("total_count", 0),
            "shares_count": raw_post.get("shares", {}).get("count", 0),
            "url": raw_post.get("permalink_url", ""),
            "facebook_type": raw_post.get("type", ""),
            "story": raw_post.get("story", ""),
            "full_picture": raw_post.get("full_picture", "")
        })
        
        return formatted_post
    
    def _determine_media_type(self, post_data: Dict[str, Any]) -> str:
        """Determina o tipo de mídia de um post do Facebook.
        
        Args:
            post_data: Dados do post
            
        Returns:
            str: Tipo de mídia (photo, video, link, status)
        """
        post_type = post_data.get("type", "")
        
        if post_type == "photo":
            return "photo"
        elif post_type == "video":
            return "video"
        elif post_type == "link":
            return "link"
        else:
            return "status"
    
    def _extract_media_url(self, post_data: Dict[str, Any]) -> str:
        """Extrai a URL da mídia de um post do Facebook.
        
        Args:
            post_data: Dados do post
            
        Returns:
            str: URL da mídia
        """
        post_type = post_data.get("type", "")
        
        if post_type == "photo" and "full_picture" in post_data:
            return post_data.get("full_picture", "")
        elif post_type == "video" and "source" in post_data:
            return post_data.get("source", "")
        elif post_type == "link" and "link" in post_data:
            return post_data.get("link", "")
        else:
            return ""