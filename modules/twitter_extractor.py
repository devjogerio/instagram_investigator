#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para extração de dados do Twitter/X
"""

import time
import logging
from datetime import datetime
from modules.twitter_api import TwitterAPI

logger = logging.getLogger(__name__)

class TwitterExtractor:
    """Classe para extração de dados do Twitter/X"""
    
    def __init__(self, bearer_token):
        """Inicializa o extrator de dados do Twitter
        
        Args:
            bearer_token: Token de autenticação da API do Twitter
        """
        self.api = TwitterAPI(bearer_token)
    
    def investigate_profile(self, username):
        """Investiga um perfil do Twitter e extrai informações detalhadas
        
        Args:
            username: Nome de usuário do Twitter (sem @)
            
        Returns:
            dict: Dados completos do perfil
            
        Raises:
            Exception: Em caso de falha na extração dos dados
        """
        try:
            # Remove @ se presente no início do username
            username = username.lstrip('@')
            
            logger.info(f"Iniciando investigação do perfil @{username} no Twitter")
            
            # Obtém dados básicos do usuário
            user_data = self.api.get_user_by_username(username)
            
            if 'data' not in user_data:
                raise Exception(f"Perfil @{username} não encontrado no Twitter")
                
            user_info = user_data['data']
            user_id = user_info['id']
            
            # Obtém tweets do usuário
            tweets_data = self.api.get_user_tweets(user_id, max_results=100)
            
            # Obtém seguidores do usuário
            followers_data = self.api.get_user_followers(user_id, max_results=100)
            
            # Obtém usuários seguidos
            following_data = self.api.get_user_following(user_id, max_results=100)
            
            # Compila todos os dados em um único objeto
            profile_data = {
                "platform": "twitter",
                "username": username,
                "user_id": user_id,
                "name": user_info.get('name', ''),
                "description": user_info.get('description', ''),
                "location": user_info.get('location', ''),
                "url": user_info.get('url', ''),
                "verified": user_info.get('verified', False),
                "created_at": user_info.get('created_at', ''),
                "profile_image_url": user_info.get('profile_image_url', ''),
                "protected": user_info.get('protected', False),
                "metrics": user_info.get('public_metrics', {}),
                "follower_count": user_info.get('public_metrics', {}).get('followers_count', 0),
                "following_count": user_info.get('public_metrics', {}).get('following_count', 0),
                "tweet_count": user_info.get('public_metrics', {}).get('tweet_count', 0),
                "listed_count": user_info.get('public_metrics', {}).get('listed_count', 0),
                "tweets": self._process_tweets(tweets_data),
                "followers": self._process_users(followers_data),
                "following": self._process_users(following_data),
                "extracted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            logger.info(f"Investigação do perfil @{username} concluída com sucesso")
            return profile_data
            
        except Exception as e:
            logger.error(f"Erro ao investigar perfil @{username}: {str(e)}")
            raise Exception(f"Falha ao extrair dados do Twitter: {str(e)}")
    
    def _process_tweets(self, tweets_data):
        """Processa dados de tweets para um formato padronizado
        
        Args:
            tweets_data: Dados brutos de tweets da API
            
        Returns:
            list: Lista de tweets processados
        """
        if 'data' not in tweets_data:
            return []
            
        processed_tweets = []
        
        for tweet in tweets_data['data']:
            processed_tweet = {
                "id": tweet.get('id', ''),
                "text": tweet.get('text', ''),
                "created_at": tweet.get('created_at', ''),
                "like_count": tweet.get('public_metrics', {}).get('like_count', 0),
                "retweet_count": tweet.get('public_metrics', {}).get('retweet_count', 0),
                "reply_count": tweet.get('public_metrics', {}).get('reply_count', 0),
                "quote_count": tweet.get('public_metrics', {}).get('quote_count', 0),
                "hashtags": self._extract_hashtags(tweet),
                "mentions": self._extract_mentions(tweet),
                "urls": self._extract_urls(tweet),
                "has_media": 'attachments' in tweet and 'media_keys' in tweet['attachments']
            }
            
            processed_tweets.append(processed_tweet)
            
        return processed_tweets
    
    def _process_users(self, users_data):
        """Processa dados de usuários para um formato padronizado
        
        Args:
            users_data: Dados brutos de usuários da API
            
        Returns:
            list: Lista de usuários processados
        """
        if 'data' not in users_data:
            return []
            
        processed_users = []
        
        for user in users_data['data']:
            processed_user = {
                "id": user.get('id', ''),
                "username": user.get('username', ''),
                "name": user.get('name', ''),
                "description": user.get('description', ''),
                "verified": user.get('verified', False),
                "profile_image_url": user.get('profile_image_url', ''),
                "follower_count": user.get('public_metrics', {}).get('followers_count', 0),
                "following_count": user.get('public_metrics', {}).get('following_count', 0),
                "tweet_count": user.get('public_metrics', {}).get('tweet_count', 0)
            }
            
            processed_users.append(processed_user)
            
        return processed_users
    
    def _extract_hashtags(self, tweet):
        """Extrai hashtags de um tweet
        
        Args:
            tweet: Dados do tweet
            
        Returns:
            list: Lista de hashtags
        """
        hashtags = []
        
        if 'entities' in tweet and 'hashtags' in tweet['entities']:
            for hashtag in tweet['entities']['hashtags']:
                hashtags.append(hashtag.get('tag', ''))
                
        return hashtags
    
    def _extract_mentions(self, tweet):
        """Extrai menções de um tweet
        
        Args:
            tweet: Dados do tweet
            
        Returns:
            list: Lista de menções
        """
        mentions = []
        
        if 'entities' in tweet and 'mentions' in tweet['entities']:
            for mention in tweet['entities']['mentions']:
                mentions.append({
                    "username": mention.get('username', ''),
                    "id": mention.get('id', '')
                })
                
        return mentions
    
    def _extract_urls(self, tweet):
        """Extrai URLs de um tweet
        
        Args:
            tweet: Dados do tweet
            
        Returns:
            list: Lista de URLs
        """
        urls = []
        
        if 'entities' in tweet and 'urls' in tweet['entities']:
            for url in tweet['entities']['urls']:
                urls.append({
                    "url": url.get('url', ''),
                    "expanded_url": url.get('expanded_url', ''),
                    "display_url": url.get('display_url', '')
                })
                
        return urls