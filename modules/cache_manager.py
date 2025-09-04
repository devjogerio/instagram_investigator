#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de gerenciamento de cache para múltiplas plataformas de redes sociais
Otimizado para Instagram, Facebook, LinkedIn, TikTok e outras plataformas
"""

import os
import json
import time
import gzip
import pickle
from datetime import datetime, timedelta
import hashlib
import logging
from typing import Dict, Any, Optional, Union

logger = logging.getLogger('instagram_investigator')

class CacheManager:
    """
    Gerencia o cache de requisições para múltiplas APIs de redes sociais
    com estratégias específicas por plataforma e otimizações avançadas
    """
    
    # Configurações específicas por plataforma
    PLATFORM_CONFIGS = {
        'instagram': {
            'default_ttl': 3600,  # 1 hora
            'profile_ttl': 7200,  # 2 horas
            'posts_ttl': 1800,    # 30 minutos
            'compression': True
        },
        'facebook': {
            'default_ttl': 5400,  # 1.5 horas
            'profile_ttl': 10800, # 3 horas
            'posts_ttl': 2700,    # 45 minutos
            'compression': True
        },
        'linkedin': {
            'default_ttl': 7200,  # 2 horas
            'profile_ttl': 14400, # 4 horas
            'posts_ttl': 3600,    # 1 hora
            'compression': True
        },
        'tiktok': {
            'default_ttl': 1800,  # 30 minutos
            'profile_ttl': 3600,  # 1 hora
            'posts_ttl': 900,     # 15 minutos
            'compression': True
        }
    }
    
    def __init__(self, cache_dir="cache", cache_duration=3600, enable_compression=True):
        """
        Inicializa o gerenciador de cache
        
        Args:
            cache_dir (str): Diretório onde os arquivos de cache serão armazenados
            cache_duration (int): Duração padrão do cache em segundos
            enable_compression (bool): Habilita compressão dos dados de cache
        """
        self.cache_dir = cache_dir
        self.default_cache_duration = cache_duration
        self.enable_compression = enable_compression
        
        # Cria estrutura de diretórios por plataforma
        self._create_cache_structure()
        
        logger.info(f"CacheManager inicializado: {cache_dir} (compressão: {enable_compression})")
    
    def _create_cache_structure(self):
        """Cria a estrutura de diretórios de cache por plataforma"""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            logger.info(f"Diretório de cache criado: {self.cache_dir}")
        
        # Cria subdiretórios para cada plataforma
        for platform in self.PLATFORM_CONFIGS.keys():
            platform_dir = os.path.join(self.cache_dir, platform)
            if not os.path.exists(platform_dir):
                os.makedirs(platform_dir)
                logger.debug(f"Diretório criado para {platform}: {platform_dir}")
    
    def _generate_cache_key(self, platform: str, endpoint: str, params: Dict = None) -> str:
        """
        Gera uma chave única para o cache baseada na plataforma, endpoint e parâmetros
        
        Args:
            platform (str): Nome da plataforma (instagram, facebook, etc.)
            endpoint (str): Endpoint da API
            params (dict): Parâmetros da requisição
            
        Returns:
            str: Chave única para o cache
        """
        # Converte parâmetros para string ordenada
        params_str = json.dumps(params, sort_keys=True) if params else ""
        
        # Cria hash MD5 da combinação plataforma + endpoint + parâmetros
        cache_string = f"{platform}_{endpoint}_{params_str}"
        cache_key = hashlib.md5(cache_string.encode()).hexdigest()
        
        return cache_key
    
    def _get_cache_file_path(self, platform: str, cache_key: str, use_compression: bool = None) -> str:
        """
        Retorna o caminho completo do arquivo de cache
        
        Args:
            platform (str): Nome da plataforma
            cache_key (str): Chave do cache
            use_compression (bool): Se deve usar compressão (None = usar configuração da plataforma)
            
        Returns:
            str: Caminho completo do arquivo
        """
        if use_compression is None:
            use_compression = self.PLATFORM_CONFIGS.get(platform, {}).get('compression', False)
        
        extension = '.gz' if use_compression else '.json'
        return os.path.join(self.cache_dir, platform, f"{cache_key}{extension}")
    
    def get(self, platform: str, endpoint: str, params: Dict = None, cache_type: str = 'default') -> Optional[Any]:
        """
        Recupera dados do cache se existirem e não estiverem expirados
        
        Args:
            platform (str): Nome da plataforma
            endpoint (str): Endpoint da API
            params (dict): Parâmetros da requisição
            cache_type (str): Tipo de cache (default, profile, posts)
            
        Returns:
            dict or None: Dados do cache ou None se não existir/expirado
        """
        try:
            cache_key = self._generate_cache_key(platform, endpoint, params)
            
            # Determina TTL baseado na plataforma e tipo
            ttl = self._get_ttl_for_platform(platform, cache_type)
            
            # Verifica compressão
            use_compression = self.PLATFORM_CONFIGS.get(platform, {}).get('compression', False)
            cache_file = self._get_cache_file_path(platform, cache_key, use_compression)
            
            # Verifica se o arquivo existe
            if not os.path.exists(cache_file):
                return None
            
            # Verifica se o cache não expirou
            file_time = os.path.getmtime(cache_file)
            current_time = time.time()
            
            if current_time - file_time > ttl:
                # Cache expirado, remove o arquivo
                os.remove(cache_file)
                logger.debug(f"Cache expirado removido: {platform}/{cache_key}")
                return None
            
            # Lê os dados do cache
            if use_compression:
                with gzip.open(cache_file, 'rb') as f:
                    data = pickle.load(f)
            else:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            logger.debug(f"Cache hit: {platform}/{cache_key}")
            return data
                
        except Exception as e:
            logger.error(f"Erro ao ler cache {platform}/{endpoint}: {str(e)}")
            return None
    
    def set(self, platform: str, endpoint: str, params: Dict, data: Any, 
            cache_type: str = 'default', ttl: int = None) -> bool:
        """
        Armazena dados no cache
        
        Args:
            platform (str): Nome da plataforma
            endpoint (str): Endpoint da API
            params (dict): Parâmetros da requisição
            data (dict): Dados a serem armazenados
            cache_type (str): Tipo de cache (default, profile, posts)
            ttl (int): TTL customizado em segundos
            
        Returns:
            bool: True se salvou com sucesso, False caso contrário
        """
        try:
            cache_key = self._generate_cache_key(platform, endpoint, params)
            
            # Usa TTL customizado ou padrão da plataforma
            if ttl is None:
                ttl = self._get_ttl_for_platform(platform, cache_type)
            
            # Verifica compressão
            use_compression = self.PLATFORM_CONFIGS.get(platform, {}).get('compression', False)
            cache_file = self._get_cache_file_path(platform, cache_key, use_compression)
            
            # Adiciona metadados aos dados
            cache_data = {
                'timestamp': time.time(),
                'ttl': ttl,
                'platform': platform,
                'endpoint': endpoint,
                'cache_type': cache_type,
                'data': data
            }
            
            # Salva os dados no arquivo
            if use_compression:
                with gzip.open(cache_file, 'wb') as f:
                    pickle.dump(cache_data, f)
            else:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    
            logger.debug(f"Dados salvos no cache: {platform}/{cache_key} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar cache {platform}/{endpoint}: {str(e)}")
            return False
    
    def clear(self, platform: str = None, endpoint: str = None, expired_only: bool = False) -> int:
        """
        Remove arquivos de cache
        
        Args:
            platform (str, optional): Se especificado, remove apenas cache desta plataforma
            endpoint (str, optional): Se especificado, remove apenas cache deste endpoint
            expired_only (bool): Se True, remove apenas arquivos expirados
                                    
        Returns:
            int: Número de arquivos removidos
        """
        removed_count = 0
        
        try:
            if platform and endpoint:
                # Remove cache específico do endpoint da plataforma
                cache_key = self._generate_cache_key(platform, endpoint, {})
                use_compression = self.PLATFORM_CONFIGS.get(platform, {}).get('compression', False)
                cache_file = self._get_cache_file_path(platform, cache_key, use_compression)
                
                if os.path.exists(cache_file):
                    os.remove(cache_file)
                    removed_count = 1
                    logger.info(f"Cache removido para {platform}/{endpoint}")
            elif platform:
                # Remove todos os caches da plataforma
                platform_dir = os.path.join(self.cache_dir, platform)
                if os.path.exists(platform_dir):
                    removed_count = self._clear_directory(platform_dir, platform, expired_only)
                    logger.info(f"Cache da plataforma {platform} limpo: {removed_count} arquivos")
            else:
                # Remove todos os arquivos de cache
                if os.path.exists(self.cache_dir):
                    for platform_name in self.PLATFORM_CONFIGS.keys():
                        platform_dir = os.path.join(self.cache_dir, platform_name)
                        if os.path.exists(platform_dir):
                            removed_count += self._clear_directory(platform_dir, platform_name, expired_only)
                    
                    # Remove arquivos na raiz (compatibilidade com versão antiga)
                    removed_count += self._clear_directory(self.cache_dir, None, expired_only, root_only=True)
                    
                    logger.info(f"Cache geral limpo: {removed_count} arquivos removidos")
                    
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {str(e)}")
            
        return removed_count
    
    def get_stats(self, platform: str = None) -> Dict[str, Any]:
        """
        Retorna estatísticas sobre o cache
        
        Args:
            platform (str, optional): Se especificado, retorna stats apenas desta plataforma
        
        Returns:
            dict: Estatísticas do cache
        """
        stats = {
            'total_files': 0,
            'total_size': 0,
            'expired_files': 0,
            'valid_files': 0,
            'platforms': {},
            'compression_ratio': 0.0
        }
        
        try:
            if platform:
                # Stats de uma plataforma específica
                platform_dir = os.path.join(self.cache_dir, platform)
                if os.path.exists(platform_dir):
                    platform_stats = self._get_directory_stats(platform_dir, platform)
                    stats.update(platform_stats)
                    stats['platforms'][platform] = platform_stats
            else:
                # Stats de todas as plataformas
                total_compressed_size = 0
                total_uncompressed_size = 0
                
                for platform_name in self.PLATFORM_CONFIGS.keys():
                    platform_dir = os.path.join(self.cache_dir, platform_name)
                    if os.path.exists(platform_dir):
                        platform_stats = self._get_directory_stats(platform_dir, platform_name)
                        stats['platforms'][platform_name] = platform_stats
                        
                        # Soma totais
                        stats['total_files'] += platform_stats['total_files']
                        stats['total_size'] += platform_stats['total_size']
                        stats['expired_files'] += platform_stats['expired_files']
                        stats['valid_files'] += platform_stats['valid_files']
                        
                        if platform_stats.get('compressed_size'):
                            total_compressed_size += platform_stats['compressed_size']
                            total_uncompressed_size += platform_stats['uncompressed_size']
                
                # Calcula taxa de compressão geral
                if total_uncompressed_size > 0:
                    stats['compression_ratio'] = 1 - (total_compressed_size / total_uncompressed_size)
                            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do cache: {str(e)}")
            
        return stats
    
    def _get_ttl_for_platform(self, platform: str, cache_type: str) -> int:
        """Retorna o TTL apropriado para a plataforma e tipo de cache"""
        platform_config = self.PLATFORM_CONFIGS.get(platform, {})
        ttl_key = f"{cache_type}_ttl"
        return platform_config.get(ttl_key, platform_config.get('default_ttl', self.default_cache_duration))
    
    def _clear_directory(self, directory: str, platform: str = None, expired_only: bool = False, root_only: bool = False) -> int:
        """Limpa arquivos de um diretório específico"""
        removed_count = 0
        current_time = time.time()
        
        for filename in os.listdir(directory):
            if root_only and not (filename.endswith('.json') or filename.endswith('.gz')):
                continue
                
            file_path = os.path.join(directory, filename)
            
            # Pula diretórios se estiver limpando a raiz
            if root_only and os.path.isdir(file_path):
                continue
                
            if os.path.isfile(file_path):
                should_remove = True
                
                if expired_only:
                    file_time = os.path.getmtime(file_path)
                    # Determina TTL baseado na plataforma se disponível
                    if platform:
                        ttl = self._get_ttl_for_platform(platform, 'default')
                    else:
                        ttl = self.default_cache_duration
                    
                    should_remove = (current_time - file_time) > ttl
                
                if should_remove:
                    os.remove(file_path)
                    removed_count += 1
        
        return removed_count
    
    def _get_directory_stats(self, directory: str, platform: str) -> Dict[str, Any]:
        """Obtém estatísticas de um diretório específico"""
        stats = {
            'total_files': 0,
            'total_size': 0,
            'expired_files': 0,
            'valid_files': 0,
            'compressed_files': 0,
            'compressed_size': 0,
            'uncompressed_size': 0
        }
        
        current_time = time.time()
        
        for filename in os.listdir(directory):
            if filename.endswith('.json') or filename.endswith('.gz'):
                file_path = os.path.join(directory, filename)
                file_size = os.path.getsize(file_path)
                file_time = os.path.getmtime(file_path)
                
                stats['total_files'] += 1
                stats['total_size'] += file_size
                
                # Verifica compressão
                if filename.endswith('.gz'):
                    stats['compressed_files'] += 1
                    stats['compressed_size'] += file_size
                    
                    # Estima tamanho descomprimido (aproximação)
                    stats['uncompressed_size'] += file_size * 3  # Estimativa conservadora
                else:
                    stats['uncompressed_size'] += file_size
                
                # Verifica expiração baseada na plataforma
                ttl = self._get_ttl_for_platform(platform, 'default')
                if current_time - file_time > ttl:
                    stats['expired_files'] += 1
                else:
                    stats['valid_files'] += 1
        
        return stats
    
    def invalidate_pattern(self, platform: str, pattern: str) -> int:
        """Invalida cache baseado em um padrão de endpoint"""
        removed_count = 0
        platform_dir = os.path.join(self.cache_dir, platform)
        
        if not os.path.exists(platform_dir):
            return 0
        
        try:
            for filename in os.listdir(platform_dir):
                if pattern in filename:
                    file_path = os.path.join(platform_dir, filename)
                    os.remove(file_path)
                    removed_count += 1
            
            logger.info(f"Invalidados {removed_count} arquivos de cache para padrão '{pattern}' em {platform}")
        except Exception as e:
            logger.error(f"Erro ao invalidar cache por padrão: {str(e)}")
        
        return removed_count