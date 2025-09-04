import unittest
import tempfile
import os
import json
import time
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.cache_manager import CacheManager

class TestCacheManager(unittest.TestCase):
    """Testes para o sistema de cache multi-plataforma"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_manager = CacheManager(cache_dir=self.temp_dir)
    
    def tearDown(self):
        """Limpeza após cada teste"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cache_set_and_get(self):
        """Testa operações básicas de set e get do cache"""
        platform = "instagram"
        cache_type = "profile"
        key = "test_user"
        data = {"username": "test_user", "followers": 1000}
        
        # Testa set
        result = self.cache_manager.set(platform, cache_type, key, data)
        self.assertTrue(result)
        
        # Testa get
        cached_data = self.cache_manager.get(platform, cache_type, key)
        self.assertEqual(cached_data, data)
    
    def test_cache_ttl_expiration(self):
        """Testa expiração do cache baseada em TTL"""
        platform = "linkedin"
        cache_type = "default"
        key = "test_key"
        data = {"test": "data"}
        ttl = 1  # 1 segundo
        
        # Define dados no cache com TTL curto
        self.cache_manager.set(platform, cache_type, key, data, ttl=ttl)
        
        # Verifica se os dados estão no cache
        cached_data = self.cache_manager.get(platform, cache_type, key)
        self.assertEqual(cached_data, data)
        
        # Aguarda expiração
        time.sleep(1.5)
        
        # Verifica se os dados expiraram
        expired_data = self.cache_manager.get(platform, cache_type, key)
        self.assertIsNone(expired_data)
    
    def test_cache_compression(self):
        """Testa compressão de dados grandes"""
        platform = "tiktok"
        cache_type = "large_data"
        key = "big_dataset"
        
        # Cria dados grandes (> 1KB para ativar compressão)
        large_data = {"data": "x" * 2000, "items": list(range(100))}
        
        # Testa set com compressão
        result = self.cache_manager.set(platform, cache_type, key, large_data)
        self.assertTrue(result)
        
        # Testa get com descompressão
        cached_data = self.cache_manager.get(platform, cache_type, key)
        self.assertEqual(cached_data, large_data)
    
    def test_cache_clear_platform(self):
        """Testa limpeza de cache por plataforma"""
        # Adiciona dados para diferentes plataformas
        self.cache_manager.set("instagram", "profile", "user1", {"data": "ig"})
        self.cache_manager.set("linkedin", "profile", "user1", {"data": "li"})
        self.cache_manager.set("tiktok", "profile", "user1", {"data": "tt"})
        
        # Limpa cache do Instagram
        self.cache_manager.clear(platform="instagram")
        
        # Verifica se apenas o Instagram foi limpo
        self.assertIsNone(self.cache_manager.get("instagram", "profile", "user1"))
        self.assertIsNotNone(self.cache_manager.get("linkedin", "profile", "user1"))
        self.assertIsNotNone(self.cache_manager.get("tiktok", "profile", "user1"))
    
    def test_cache_clear_all(self):
        """Testa limpeza completa do cache"""
        # Adiciona dados para diferentes plataformas
        self.cache_manager.set("instagram", "profile", "user1", {"data": "ig"})
        self.cache_manager.set("linkedin", "profile", "user1", {"data": "li"})
        
        # Limpa todo o cache
        self.cache_manager.clear()
        
        # Verifica se tudo foi limpo
        self.assertIsNone(self.cache_manager.get("instagram", "profile", "user1"))
        self.assertIsNone(self.cache_manager.get("linkedin", "profile", "user1"))
    
    def test_cache_invalid_data(self):
        """Testa comportamento com dados inválidos"""
        platform = "instagram"
        cache_type = "profile"
        key = "test_key"
        
        # Testa com dados não serializáveis
        invalid_data = {"func": lambda x: x}  # Função não é serializável
        result = self.cache_manager.set(platform, cache_type, key, invalid_data)
        self.assertFalse(result)
    
    def test_cache_stats(self):
        """Testa estatísticas do cache"""
        # Adiciona alguns dados
        self.cache_manager.set("instagram", "profile", "user1", {"data": "test1"})
        self.cache_manager.set("linkedin", "profile", "user2", {"data": "test2"})
        
        # Faz algumas consultas
        self.cache_manager.get("instagram", "profile", "user1")  # Hit
        self.cache_manager.get("instagram", "profile", "nonexistent")  # Miss
        
        stats = self.cache_manager.get_stats()
        
        self.assertIn("total_entries", stats)
        self.assertIn("cache_hits", stats)
        self.assertIn("cache_misses", stats)
        self.assertIn("hit_rate", stats)
        
        self.assertEqual(stats["total_entries"], 2)
        self.assertEqual(stats["cache_hits"], 1)
        self.assertEqual(stats["cache_misses"], 1)
        self.assertEqual(stats["hit_rate"], 0.5)

if __name__ == '__main__':
    unittest.main()