import os
import time
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

from modules.linkedin_api import LinkedInAPI
from modules.base_extractor import BaseExtractor

class LinkedInExtractor(BaseExtractor):
    """
    Classe para extrair e processar dados do LinkedIn.
    Utiliza a API do LinkedIn para obter dados e os processa em um formato padronizado.
    Herda de BaseExtractor para seguir padrões comuns.
    """
    
    def __init__(self, cache_manager=None):
        """
        Inicializa o extrator do LinkedIn.
        
        Args:
            cache_manager: Gerenciador de cache opcional para armazenar respostas
        """
        super().__init__("linkedin")
        self.api = LinkedInAPI(cache_manager=cache_manager)
        self.cache_manager = cache_manager
    
    def extract_profile(self, username: str) -> Dict[str, Any]:
        """
        Extrai informações do perfil do LinkedIn.
        
        Args:
            username: Nome de usuário ou ID do perfil do LinkedIn
            
        Returns:
            Dict: Dados estruturados do perfil
        """
        if not self.validate_username(username):
            return self.handle_error(ValueError("Nome de usuário inválido"), "validação")
        
        self.log_extraction_start(username, "extração de perfil")
        
        try:
            # Determinar se é um ID ou um nome personalizado
            if username.startswith('urn:li:person:') or username == 'me':
                profile_data = self.api.get_profile(username)
            else:
                profile_data = self.api.get_profile_by_vanity_name(username)
            
            # Obter dados adicionais
            connections = self.api.get_connections(profile_data.get('id', 'me'))
            
            # Processar e estruturar os dados
            structured_data = self._process_profile_data(profile_data, connections)
            
            self.log_extraction_end(username, True, "extração de perfil")
            return structured_data
            
        except Exception as e:
            self.log_extraction_end(username, False, "extração de perfil")
            return self.handle_error(e, "extração de perfil")
    
    def extract_posts(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Extrai posts do perfil do LinkedIn.
        
        Args:
            username: Nome de usuário ou ID do perfil do LinkedIn
            limit: Número máximo de posts a serem extraídos
            
        Returns:
            List[Dict]: Lista de posts extraídos
        """
        if not self.validate_username(username):
            return []
        
        self.log_extraction_start(username, "extração de posts")
        
        try:
            # Determinar se é um ID ou um nome personalizado
            if username.startswith('urn:li:person:') or username == 'me':
                user_id = username
            else:
                profile_data = self.api.get_profile_by_vanity_name(username)
                user_id = profile_data.get('id', 'me')
            
            # Obter posts
            posts_data = self.api.get_posts(user_id, count=limit)
            posts_list = self._process_posts(posts_data.get('elements', []))
            
            self.log_extraction_end(username, True, "extração de posts")
            return posts_list
            
        except Exception as e:
            self.log_extraction_end(username, False, "extração de posts")
            self.logger.error(f"Erro ao extrair posts: {str(e)}")
            return []
    
    def investigate_profile(self, profile_identifier: str) -> Dict[str, Any]:
        """
        Investiga um perfil do LinkedIn e retorna dados estruturados (método legado).
        
        Args:
            profile_identifier: ID do perfil ou nome personalizado da URL
            
        Returns:
            Dict: Dados estruturados do perfil
        """
        # Redireciona para o método padrão extract_profile
        return self.extract_profile(profile_identifier)
    
    def _process_profile_data(self, profile_data: Dict, connections: Dict) -> Dict[str, Any]:
        """
        Processa os dados brutos do perfil em um formato estruturado.
        
        Args:
            profile_data: Dados brutos do perfil
            connections: Dados das conexões
            
        Returns:
            Dict: Dados estruturados do perfil
        """
        try:
            # Extrair informações básicas do perfil
            profile_id = profile_data.get('id', '')
            
            # Processar nome completo
            first_name = self._extract_localized_string(profile_data.get('firstName', {}))
            last_name = self._extract_localized_string(profile_data.get('lastName', {}))
            full_name = f"{first_name} {last_name}".strip()
            
            # Extrair foto do perfil
            profile_picture = self._extract_profile_picture(profile_data)
            
            # Extrair experiências profissionais
            positions = self._process_positions(profile_data.get('positions', {}).get('elements', []))
            
            # Extrair formação acadêmica
            educations = self._process_educations(profile_data.get('educations', {}).get('elements', []))
            
            # Extrair habilidades
            skills = self._process_skills(profile_data.get('skills', {}).get('elements', []))
            
            # Processar conexões
            connection_count = connections.get('paging', {}).get('total', 0)
            connection_list = self._process_connections(connections.get('elements', []))
            
            # Usar o formato padronizado da BaseExtractor
            return self.format_standard_profile(
                username=profile_data.get('vanityName', profile_id),
                full_name=full_name,
                bio=profile_data.get('summary', ''),
                followers_count=connection_count,
                following_count=0,  # LinkedIn não fornece essa informação diretamente
                posts_count=0,  # Será obtido separadamente
                profile_picture_url=profile_picture,
                is_verified=False,  # LinkedIn não tem verificação como outras redes
                is_private=False,  # Assumindo público se conseguimos acessar
                external_url=f"https://www.linkedin.com/in/{profile_data.get('vanityName', profile_id)}/",
                location=profile_data.get('locationName', ''),
                additional_info={
                    'headline': profile_data.get('headline', ''),
                    'industry': profile_data.get('industryName', ''),
                    'positions': positions,
                    'educations': educations,
                    'skills': skills,
                    'connections': connection_list
                },
                raw_data={
                    'profile': profile_data,
                    'connections': connections
                }
            )
            
        except Exception as e:
            return self.handle_error(e, "processamento de dados do perfil")
    
    def _extract_localized_string(self, localized_data: Dict) -> str:
        """
        Extrai string localizada dos dados do LinkedIn.
        
        Args:
            localized_data: Dados localizados
            
        Returns:
            str: String localizada
        """
        if not localized_data or 'localized' not in localized_data:
            return ''
        
        # Tentar obter a string em português primeiro
        localized = localized_data.get('localized', {})
        if 'pt_BR' in localized:
            return localized['pt_BR']
        elif 'en_US' in localized:
            return localized['en_US']
        elif localized:
            # Retornar o primeiro valor disponível
            return next(iter(localized.values()))
        
        return ''
    
    def _extract_profile_picture(self, profile_data: Dict) -> str:
        """
        Extrai a URL da foto do perfil.
        
        Args:
            profile_data: Dados do perfil
            
        Returns:
            str: URL da foto do perfil
        """
        try:
            if 'profilePicture' in profile_data and 'displayImage~' in profile_data['profilePicture']:
                elements = profile_data['profilePicture']['displayImage~'].get('elements', [])
                if elements:
                    # Obter a imagem de maior resolução
                    for element in sorted(elements, key=lambda x: x.get('data', {}).get('width', 0), reverse=True):
                        identifiers = element.get('identifiers', [])
                        if identifiers:
                            return identifiers[0].get('identifier', '')
        except Exception:
            pass
        
        return ''
    
    def _process_positions(self, positions: List[Dict]) -> List[Dict]:
        """
        Processa as experiências profissionais.
        
        Args:
            positions: Lista de experiências profissionais
            
        Returns:
            List[Dict]: Lista processada de experiências
        """
        processed_positions = []
        
        for position in positions:
            company_name = ''
            if 'company' in position:
                company_name = position['company'].get('name', '')
            
            title = self._extract_localized_string(position.get('title', {}))
            
            # Processar datas
            start_date = self._format_date(position.get('startDate', {}))
            end_date = self._format_date(position.get('endDate', {})) if 'endDate' in position else 'Presente'
            
            processed_positions.append({
                'title': title,
                'company': company_name,
                'location': position.get('location', ''),
                'start_date': start_date,
                'end_date': end_date,
                'description': position.get('description', ''),
                'is_current': position.get('isCurrent', False)
            })
        
        return processed_positions
    
    def _process_educations(self, educations: List[Dict]) -> List[Dict]:
        """
        Processa as formações acadêmicas.
        
        Args:
            educations: Lista de formações acadêmicas
            
        Returns:
            List[Dict]: Lista processada de formações
        """
        processed_educations = []
        
        for education in educations:
            school_name = ''
            if 'school' in education:
                school_name = education['school'].get('name', '')
            
            degree = self._extract_localized_string(education.get('degreeName', {}))
            field_of_study = self._extract_localized_string(education.get('fieldOfStudy', {}))
            
            # Processar datas
            start_date = self._format_date(education.get('startDate', {}))
            end_date = self._format_date(education.get('endDate', {})) if 'endDate' in education else 'Presente'
            
            processed_educations.append({
                'school': school_name,
                'degree': degree,
                'field_of_study': field_of_study,
                'start_date': start_date,
                'end_date': end_date,
                'description': education.get('description', '')
            })
        
        return processed_educations
    
    def _process_skills(self, skills: List[Dict]) -> List[str]:
        """
        Processa as habilidades.
        
        Args:
            skills: Lista de habilidades
            
        Returns:
            List[str]: Lista processada de habilidades
        """
        processed_skills = []
        
        for skill in skills:
            if 'name' in skill:
                processed_skills.append(skill['name'])
        
        return processed_skills
    
    def _process_connections(self, connections: List[Dict]) -> List[Dict]:
        """
        Processa as conexões.
        
        Args:
            connections: Lista de conexões
            
        Returns:
            List[Dict]: Lista processada de conexões
        """
        processed_connections = []
        
        for connection in connections:
            first_name = self._extract_localized_string(connection.get('firstName', {}))
            last_name = self._extract_localized_string(connection.get('lastName', {}))
            full_name = f"{first_name} {last_name}".strip()
            
            profile_picture = ''
            if 'profilePicture' in connection and 'displayImage~' in connection['profilePicture']:
                elements = connection['profilePicture']['displayImage~'].get('elements', [])
                if elements and 'identifiers' in elements[0]:
                    profile_picture = elements[0]['identifiers'][0].get('identifier', '')
            
            processed_connections.append({
                'id': connection.get('id', ''),
                'name': full_name,
                'headline': connection.get('headline', ''),
                'profile_picture': profile_picture
            })
        
        return processed_connections
    
    def _process_posts(self, posts: List[Dict]) -> List[Dict[str, Any]]:
        """
        Processa uma lista de posts do LinkedIn usando o formato padronizado.
        
        Args:
            posts: Lista de posts brutos
            
        Returns:
            List[Dict]: Lista de posts processados
        """
        processed_posts = []
        
        for post in posts:
            try:
                # Extrair informações básicas do post
                post_id = post.get('id', '')
                
                # Extrair conteúdo do post
                content = ''
                if 'commentary' in post:
                    content = post['commentary'].get('text', '')
                
                # Extrair data de publicação
                created_time = datetime.fromtimestamp(post.get('created', {}).get('time', 0) / 1000).isoformat() \
                    if 'created' in post and 'time' in post['created'] else ''
                
                # Extrair estatísticas de engajamento
                likes = post.get('likesSummary', {}).get('totalLikes', 0)
                comments = post.get('commentsSummary', {}).get('totalComments', 0)
                shares = post.get('sharesSummary', {}).get('totalShares', 0) if 'sharesSummary' in post else 0
                
                # Usar o formato padronizado da BaseExtractor
                processed_post = self.format_standard_post(
                    post_id=post_id,
                    content=content,
                    created_at=created_time,
                    likes_count=likes,
                    comments_count=comments,
                    shares_count=shares,
                    media_urls=[],
                    hashtags=self._extract_hashtags(content),
                    mentions=self._extract_mentions(content),
                    post_url=f"https://www.linkedin.com/feed/update/{post_id}/",
                    additional_info={
                        'total_engagement': likes + comments + shares
                    },
                    raw_data=post
                )
                
                processed_posts.append(processed_post)
                
            except Exception as e:
                self.logger.warning(f"Erro ao processar post {post.get('id', 'unknown')}: {str(e)}")
                continue
        
        return processed_posts
    
    def _extract_hashtags(self, content: str) -> List[str]:
        """
        Extrai hashtags do conteúdo do post.
        
        Args:
            content: Conteúdo do post
            
        Returns:
            List[str]: Lista de hashtags encontradas
        """
        import re
        if not content:
            return []
        
        hashtags = re.findall(r'#\w+', content)
        return [tag.lower() for tag in hashtags]
    
    def _extract_mentions(self, content: str) -> List[str]:
        """
        Extrai menções do conteúdo do post.
        
        Args:
            content: Conteúdo do post
            
        Returns:
            List[str]: Lista de menções encontradas
        """
        import re
        if not content:
            return []
        
        mentions = re.findall(r'@\w+', content)
        return [mention.lower() for mention in mentions]
    
    def _calculate_engagement_metrics(self, posts: List[Dict]) -> Dict[str, Any]:
        """
        Calcula métricas de engajamento com base nas publicações.
        
        Args:
            posts: Lista de publicações processadas no formato padronizado
            
        Returns:
            Dict: Métricas de engajamento
        """
        if not posts:
            return {
                'avg_likes': 0,
                'avg_comments': 0,
                'avg_shares': 0,
                'avg_engagement': 0,
                'total_likes': 0,
                'total_comments': 0,
                'total_shares': 0,
                'total_engagement': 0
            }
        
        # Usar o formato padronizado dos posts
        total_likes = sum(post.get('likes_count', 0) for post in posts)
        total_comments = sum(post.get('comments_count', 0) for post in posts)
        total_shares = sum(post.get('shares_count', 0) for post in posts)
        total_engagement = total_likes + total_comments + total_shares
        
        post_count = len(posts)
        
        return {
            'avg_likes': total_likes / post_count,
            'avg_comments': total_comments / post_count,
            'avg_shares': total_shares / post_count,
            'avg_engagement': total_engagement / post_count,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'total_engagement': total_engagement
        }
    
    def _format_date(self, date_dict: Dict) -> str:
        """
        Formata um dicionário de data do LinkedIn em string.
        
        Args:
            date_dict: Dicionário de data (ano, mês, dia)
            
        Returns:
            str: Data formatada
        """
        if not date_dict:
            return ''
        
        year = date_dict.get('year', 0)
        month = date_dict.get('month', 0)
        day = date_dict.get('day', 0)
        
        if year and month and day:
            return f"{day:02d}/{month:02d}/{year}"
        elif year and month:
            return f"{month:02d}/{year}"
        elif year:
            return str(year)
        
        return ''