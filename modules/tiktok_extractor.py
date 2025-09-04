import os
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from modules.tiktok_api import TikTokAPI
from modules.base_extractor import BaseExtractor

class TikTokExtractor(BaseExtractor):
    """
    Classe para extrair e processar dados do TikTok.
    Utiliza a API do TikTok para obter dados e os processa em um formato padronizado.
    """
    
    def __init__(self, cache_manager=None):
        """
        Inicializa o extrator do TikTok.
        
        Args:
            cache_manager: Gerenciador de cache opcional para armazenar respostas
        """
        super().__init__("tiktok")
        self.api = TikTokAPI(cache_manager=cache_manager)
        self.cache_manager = cache_manager
    
    def extract_profile(self, username: str) -> Dict[str, Any]:
        """
        Extrai dados do perfil do TikTok.
        
        Args:
            username: Nome de usuário do TikTok
            
        Returns:
            Dict: Dados padronizados do perfil
        """
        # Validar nome de usuário
        if not self.validate_username(username):
            return {
                'success': False,
                'error': 'Nome de usuário inválido',
                'platform': self.platform
            }
        
        # Registrar início da extração
        self.log_extraction_start(username)
        
        try:
            # Obter informações do usuário
            user_info = self.api.get_user_info(username)
            
            # Verificar se a resposta contém dados do usuário
            if not user_info or 'data' not in user_info or 'user' not in user_info['data']:
                return {
                    'success': False,
                    'error': 'Usuário não encontrado',
                    'platform': self.platform
                }
            
            user_data = user_info['data']['user']
            
            # Processar dados do perfil
            profile_data = self._process_profile_data(user_data)
            
            # Registrar fim da extração
            self.log_extraction_end(username, True)
            
            return profile_data
            
        except Exception as e:
            error_msg = self.handle_error(e, f"Erro ao extrair perfil do TikTok para {username}")
            self.log_extraction_end(username, False, error_msg)
            return {
                'success': False,
                'error': error_msg,
                'platform': self.platform
            }
    
    def extract_posts(self, username: str, max_posts: int = 50) -> Dict[str, Any]:
        """
        Extrai posts/vídeos do usuário do TikTok.
        
        Args:
            username: Nome de usuário do TikTok
            max_posts: Número máximo de posts a extrair
            
        Returns:
            Dict: Dados padronizados dos posts
        """
        # Validar nome de usuário
        if not self.validate_username(username):
            return {
                'success': False,
                'error': 'Nome de usuário inválido',
                'platform': self.platform
            }
        
        try:
            # Obter informações do usuário primeiro para pegar o ID
            user_info = self.api.get_user_info(username)
            
            if not user_info or 'data' not in user_info or 'user' not in user_info['data']:
                return {
                    'success': False,
                    'error': 'Usuário não encontrado',
                    'platform': self.platform
                }
            
            user_data = user_info['data']['user']
            user_id = user_data.get('id')
            
            # Obter vídeos do usuário
            videos_data = self.api.get_user_videos(user_id, max_count=max_posts)
            videos = videos_data.get('data', {}).get('videos', [])
            
            # Processar posts
            processed_posts = self._process_posts(videos)
            
            return {
                'success': True,
                'platform': self.platform,
                'username': username,
                'posts': processed_posts,
                'total_posts': len(processed_posts),
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = self.handle_error(e, f"Erro ao extrair posts do TikTok para {username}")
            return {
                'success': False,
                'error': error_msg,
                'platform': self.platform
            }
    
    def investigate_profile(self, username: str) -> Dict[str, Any]:
        """
        Método legado - redireciona para extract_profile.
        
        Args:
            username: Nome de usuário do TikTok
            
        Returns:
            Dict: Dados estruturados do perfil
        """
        return self.extract_profile(username)
    
    def _process_profile_data(self, user_data: Dict) -> Dict[str, Any]:
        """
        Processa os dados brutos do perfil em um formato padronizado.
        
        Args:
            user_data: Dados brutos do usuário
            
        Returns:
            Dict: Dados padronizados do perfil
        """
        try:
            # Extrair informações básicas do perfil
            username = user_data.get('username', '')
            full_name = user_data.get('display_name', '')
            bio = user_data.get('bio_description', '')
            profile_picture = user_data.get('avatar_url', '')
            
            # Extrair métricas do perfil
            follower_count = user_data.get('follower_count', 0)
            following_count = user_data.get('following_count', 0)
            video_count = user_data.get('video_count', 0)
            
            # Dados adicionais específicos do TikTok
            additional_data = {
                'profile_id': user_data.get('id', ''),
                'video_count': video_count,
                'total_likes': user_data.get('total_favorited', 0),
                'verified': user_data.get('verified', False)
            }
            
            # Usar o formato padronizado da BaseExtractor
            return self.format_standard_profile(
                username=username,
                full_name=full_name,
                bio=bio,
                follower_count=follower_count,
                following_count=following_count,
                profile_picture_url=profile_picture,
                profile_url=f"https://www.tiktok.com/@{username}",
                location=None,  # TikTok não fornece localização pública
                additional_data=additional_data,
                raw_data=user_data
            )
            
        except Exception as e:
             raise Exception(f"Erro ao processar dados do perfil: {str(e)}")
    
    def _process_posts(self, videos: List[Dict]) -> List[Dict]:
        """
        Processa os vídeos/posts do usuário usando o formato padronizado.
        
        Args:
            videos: Lista de vídeos brutos
            
        Returns:
            List[Dict]: Lista de posts padronizados
        """
        processed_posts = []
        
        for video in videos:
            try:
                # Extrair informações básicas do vídeo
                post_id = video.get('id', '')
                content = video.get('description', '')
                created_at = self._format_date(video.get('create_time'))
                
                # Extrair métricas de engajamento
                likes_count = video.get('like_count', 0)
                comments_count = video.get('comment_count', 0)
                shares_count = video.get('share_count', 0)
                views_count = video.get('view_count', 0)
                
                # Extrair URLs de mídia
                media_urls = []
                if video.get('share_url'):
                    media_urls.append(video['share_url'])
                if video.get('cover_image_url'):
                    media_urls.append(video['cover_image_url'])
                
                # Extrair hashtags e menções
                hashtags = self._extract_hashtags(content)
                mentions = self._extract_mentions(content)
                
                # Dados adicionais específicos do TikTok
                additional_data = {
                    'duration': video.get('duration', 0),
                    'view_count': views_count,
                    'cover_image': video.get('cover_image_url', ''),
                    'sound': self._extract_sound_info(video)
                }
                
                # Usar o formato padronizado da BaseExtractor
                post_data = self.format_standard_post(
                    post_id=post_id,
                    content=content,
                    created_at=created_at,
                    likes_count=likes_count,
                    comments_count=comments_count,
                    shares_count=shares_count,
                    media_urls=media_urls,
                    hashtags=hashtags,
                    mentions=mentions,
                    additional_data=additional_data,
                    raw_data=video
                )
                
                processed_posts.append(post_data)
                
            except Exception as e:
                # Log do erro mas continua processando outros posts
                print(f"Erro ao processar post {video.get('id', 'unknown')}: {str(e)}")
                continue
        
        return processed_posts
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """
        Extrai hashtags do conteúdo do post.
        
        Args:
            content: Conteúdo do post
            
        Returns:
            List[str]: Lista de hashtags (sem o #)
        """
        import re
        hashtags = re.findall(r'#(\w+)', content)
        return [tag.lower() for tag in hashtags]
    
    def _extract_mentions(self, content: str) -> List[str]:
        """
        Extrai menções do conteúdo do post.
        
        Args:
            content: Conteúdo do post
            
        Returns:
            List[str]: Lista de menções (sem o @)
        """
        import re
        mentions = re.findall(r'@(\w+)', content)
        return [mention.lower() for mention in mentions]
    
    def _format_date(self, timestamp) -> str:
        """
        Formata timestamp para string ISO.
        
        Args:
            timestamp: Timestamp Unix ou None
            
        Returns:
            str: Data formatada em ISO ou string vazia
        """
        if timestamp:
            try:
                return datetime.fromtimestamp(timestamp).isoformat()
            except (ValueError, TypeError):
                return ''
        return ''
    
    def _extract_sound_info(self, video: Dict) -> Dict:
        """
        Extrai informações de som/música do vídeo.
        
        Args:
            video: Dados brutos do vídeo
            
        Returns:
            Dict: Informações do som
        """
        if 'music' in video and video['music']:
            return {
                'id': video['music'].get('id', ''),
                'title': video['music'].get('title', ''),
                'author': video['music'].get('author', ''),
                'duration': video['music'].get('duration', 0)
            }
        return {}
    
    def _process_videos(self, videos: List[Dict]) -> List[Dict]:
        """
        Processa os vídeos do usuário.
        
        Args:
            videos: Lista de vídeos
            
        Returns:
            List[Dict]: Lista processada de vídeos
        """
        processed_videos = []
        
        for video in videos:
            # Extrair informações básicas do vídeo
            video_id = video.get('id', '')
            description = video.get('description', '')
            create_time = datetime.fromtimestamp(video.get('create_time', 0)).isoformat() \
                if 'create_time' in video else ''
            
            # Extrair métricas de engajamento
            view_count = video.get('view_count', 0)
            like_count = video.get('like_count', 0)
            comment_count = video.get('comment_count', 0)
            share_count = video.get('share_count', 0)
            
            # Extrair informações de mídia
            duration = video.get('duration', 0)
            cover_image = video.get('cover_image_url', '')
            video_url = video.get('share_url', '')
            
            # Extrair hashtags
            hashtags = []
            if 'hashtags' in video:
                hashtags = [tag.get('name', '') for tag in video['hashtags']]
            
            # Extrair informações de som/música
            sound = {}
            if 'music' in video:
                sound = {
                    'id': video['music'].get('id', ''),
                    'title': video['music'].get('title', ''),
                    'author': video['music'].get('author', ''),
                    'duration': video['music'].get('duration', 0)
                }
            
            processed_videos.append({
                'id': video_id,
                'description': description,
                'created_at': create_time,
                'view_count': view_count,
                'like_count': like_count,
                'comment_count': comment_count,
                'share_count': share_count,
                'total_engagement': like_count + comment_count + share_count,
                'duration': duration,
                'cover_image': cover_image,
                'video_url': video_url,
                'hashtags': hashtags,
                'sound': sound
            })
        
        return processed_videos
    
    def _process_users(self, users: List[Dict]) -> List[Dict]:
        """
        Processa a lista de usuários (seguidores ou seguindo).
        
        Args:
            users: Lista de usuários
            
        Returns:
            List[Dict]: Lista processada de usuários
        """
        processed_users = []
        
        for user in users:
            processed_users.append({
                'id': user.get('id', ''),
                'username': user.get('username', ''),
                'display_name': user.get('display_name', ''),
                'avatar': user.get('avatar_url', ''),
                'follower_count': user.get('follower_count', 0),
                'bio': user.get('bio_description', '')
            })
        
        return processed_users
    
    def _calculate_engagement_metrics(self, videos: List[Dict]) -> Dict:
        """
        Calcula métricas de engajamento com base nos vídeos.
        
        Args:
            videos: Lista de vídeos processados
            
        Returns:
            Dict: Métricas de engajamento
        """
        if not videos:
            return {
                'avg_views': 0,
                'avg_likes': 0,
                'avg_comments': 0,
                'avg_shares': 0,
                'avg_engagement_rate': 0,
                'total_views': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_shares': 0
            }
        
        total_views = sum(video.get('additional_data', {}).get('view_count', 0) for video in videos)
        total_likes = sum(video.get('likes_count', 0) for video in videos)
        total_comments = sum(video.get('comments_count', 0) for video in videos)
        total_shares = sum(video.get('shares_count', 0) for video in videos)
        
        video_count = len(videos)
        
        avg_views = total_views / video_count
        avg_likes = total_likes / video_count
        avg_comments = total_comments / video_count
        avg_shares = total_shares / video_count
        
        # Calcular taxa de engajamento média (likes + comentários + compartilhamentos) / visualizações
        avg_engagement_rate = 0
        if total_views > 0:
            avg_engagement_rate = ((total_likes + total_comments + total_shares) / total_views) * 100
        
        return {
            'avg_views': avg_views,
            'avg_likes': avg_likes,
            'avg_comments': avg_comments,
            'avg_shares': avg_shares,
            'avg_engagement_rate': avg_engagement_rate,
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares
        }
    
    def _extract_common_hashtags(self, videos: List[Dict]) -> List[Dict]:
        """
        Extrai as hashtags mais comuns dos vídeos.
        
        Args:
            videos: Lista de vídeos processados
            
        Returns:
            List[Dict]: Lista das hashtags mais comuns
        """
        hashtag_count = {}
        
        # Contar ocorrências de cada hashtag
        for video in videos:
            for hashtag in video.get('hashtags', []):
                if hashtag in hashtag_count:
                    hashtag_count[hashtag] += 1
                else:
                    hashtag_count[hashtag] = 1
        
        # Ordenar por contagem e retornar as 10 mais comuns
        common_hashtags = [{'name': tag, 'count': count} 
                          for tag, count in sorted(hashtag_count.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        return common_hashtags
    
    def _extract_common_sounds(self, videos: List[Dict]) -> List[Dict]:
        """
        Extrai os sons/músicas mais comuns dos vídeos.
        
        Args:
            videos: Lista de vídeos brutos
            
        Returns:
            List[Dict]: Lista dos sons mais comuns
        """
        sound_count = {}
        sound_details = {}
        
        # Contar ocorrências de cada som e armazenar detalhes
        for video in videos:
            if 'music' in video and 'id' in video['music']:
                sound_id = video['music']['id']
                
                if sound_id in sound_count:
                    sound_count[sound_id] += 1
                else:
                    sound_count[sound_id] = 1
                    sound_details[sound_id] = {
                        'id': sound_id,
                        'title': video['music'].get('title', ''),
                        'author': video['music'].get('author', '')
                    }
        
        # Ordenar por contagem e retornar os 5 mais comuns
        common_sounds = []
        for sound_id, count in sorted(sound_count.items(), key=lambda x: x[1], reverse=True)[:5]:
            sound_info = sound_details[sound_id]
            sound_info['count'] = count
            common_sounds.append(sound_info)
        
        return common_sounds
    
    def get_video_details(self, video_id: str) -> Dict[str, Any]:
        """
        Obtém detalhes completos de um vídeo específico.
        
        Args:
            video_id: ID do vídeo
            
        Returns:
            Dict: Detalhes completos do vídeo
        """
        try:
            # Obter informações do vídeo
            video_info = self.api.get_video_info(video_id)
            
            if not video_info or 'data' not in video_info or 'video' not in video_info['data']:
                return {
                    'success': False,
                    'error': 'Vídeo não encontrado',
                    'platform': 'tiktok'
                }
            
            video_data = video_info['data']['video']
            
            # Obter comentários do vídeo
            comments_data = self.api.get_video_comments(video_id, max_count=50)
            comments = comments_data.get('data', {}).get('comments', [])
            
            # Processar dados do vídeo
            processed_video = self._process_videos([video_data])[0]
            
            # Processar comentários
            processed_comments = []
            for comment in comments:
                processed_comments.append({
                    'id': comment.get('id', ''),
                    'text': comment.get('text', ''),
                    'create_time': datetime.fromtimestamp(comment.get('create_time', 0)).isoformat() \
                        if 'create_time' in comment else '',
                    'like_count': comment.get('like_count', 0),
                    'user': {
                        'id': comment.get('user', {}).get('id', ''),
                        'username': comment.get('user', {}).get('username', ''),
                        'display_name': comment.get('user', {}).get('display_name', ''),
                        'avatar': comment.get('user', {}).get('avatar_url', '')
                    }
                })
            
            # Adicionar comentários ao resultado
            processed_video['comments'] = processed_comments
            processed_video['comment_count'] = len(processed_comments)
            
            return {
                'success': True,
                'platform': 'tiktok',
                'video': processed_video,
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'tiktok'
            }
    
    def search_hashtag(self, hashtag: str, max_videos: int = 20) -> Dict[str, Any]:
        """
        Pesquisa vídeos por hashtag.
        
        Args:
            hashtag: Hashtag a ser pesquisada (sem o #)
            max_videos: Número máximo de vídeos a retornar
            
        Returns:
            Dict: Resultados da pesquisa
        """
        try:
            # Obter informações da hashtag
            hashtag_info = self.api.get_hashtag_info(hashtag)
            
            if not hashtag_info or 'data' not in hashtag_info or 'hashtag' not in hashtag_info['data']:
                return {
                    'success': False,
                    'error': 'Hashtag não encontrada',
                    'platform': 'tiktok'
                }
            
            hashtag_data = hashtag_info['data']['hashtag']
            hashtag_id = hashtag_data.get('id')
            
            # Obter vídeos da hashtag
            videos_data = self.api.get_hashtag_videos(hashtag_id, max_count=max_videos)
            videos = videos_data.get('data', {}).get('videos', [])
            
            # Processar vídeos
            processed_videos = self._process_videos(videos)
            
            return {
                'success': True,
                'platform': 'tiktok',
                'hashtag': {
                    'id': hashtag_id,
                    'name': hashtag_data.get('name', ''),
                    'video_count': hashtag_data.get('video_count', 0),
                    'view_count': hashtag_data.get('view_count', 0)
                },
                'videos': processed_videos,
                'extracted_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'platform': 'tiktok'
            }