import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import requests
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.instagram_api import InstagramAPI
from modules.linkedin_api import LinkedInAPI
from modules.tiktok_api import TikTokAPI

class TestInstagramAPI(unittest.TestCase):
    """Testes para a API do Instagram"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        with patch('modules.cache_manager.CacheManager') as mock_cache:
            # Configura o mock do cache para retornar None por padrão
            mock_cache.get.return_value = None
            mock_cache.set.return_value = None
            self.api = InstagramAPI('test_session_id', mock_cache)
    
    @patch('requests.get')
    def test_get_user_id_success(self, mock_get):
        """Testa obtenção bem-sucedida do ID do usuário"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "user": {
                    "id": "123456789",
                    "username": "test_user"
                }
            }
        }
        mock_get.return_value = mock_response
        
        # Testa a função
        result = self.api.get_user_id('test_user')
        self.assertEqual(result['id'], '123456789')
    
    @patch('requests.get')
    def test_get_user_id_not_found(self, mock_get):
        """Testa comportamento quando usuário não é encontrado"""
        # Mock da resposta de erro
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Testa a função
        result = self.api.get_user_id('nonexistent_user')
        self.assertEqual(result['error'], 'Usuário não encontrado')
    
    @patch('requests.get')
    def test_get_user_info_success(self, mock_get):
        """Testa obtenção bem-sucedida de informações do usuário"""
        # Mock da resposta da API
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "user": {
                "id": "123456789",
                "username": "test_user",
                "full_name": "Test User",
                "biography": "Test bio",
                "edge_followed_by": {"count": 1000},
                "edge_follow": {"count": 500},
                "edge_owner_to_timeline_media": {"count": 100}
            }
        }
        mock_get.return_value = mock_response
        
        # Testa a função
        result = self.api.get_user_info('123456789')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['user']['username'], 'test_user')

class TestLinkedInAPI(unittest.TestCase):
    """Testes para a API do LinkedIn"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        with patch('modules.cache_manager.CacheManager'):
            self.api = LinkedInAPI()
    
    @patch.object(LinkedInAPI, '_make_request')
    def test_get_profile_success(self, mock_make_request):
        """Testa obtenção bem-sucedida do perfil"""
        # Mock da resposta da API
        mock_make_request.return_value = {
            "id": "test-user",
            "firstName": {"localized": {"en_US": "Test"}},
            "lastName": {"localized": {"en_US": "User"}},
            "headline": {"localized": {"en_US": "Software Engineer"}},
            "summary": {"localized": {"en_US": "Test bio"}}
        }
        
        # Testa a função
        profile = self.api.get_profile('test-user')
        
        self.assertIsNotNone(profile)
        self.assertEqual(profile['id'], 'test-user')
    
    @patch.object(LinkedInAPI, '_make_request')
    def test_get_profile_not_found(self, mock_make_request):
        """Testa comportamento quando perfil não é encontrado"""
        # Mock da resposta de erro
        mock_make_request.side_effect = Exception("Perfil não encontrado")
        
        # Testa a função
        with self.assertRaises(Exception):
            self.api.get_profile('nonexistent-user')
    
    @patch.object(LinkedInAPI, '_make_request')
    def test_get_company_info_success(self, mock_make_request):
        """Testa obtenção bem-sucedida de informações da empresa"""
        # Mock da resposta da API
        mock_make_request.return_value = {
            "id": 12345,
            "name": "Test Company",
            "description": "A test company",
            "industry": "Technology",
            "employeeCount": 1000
        }
        
        # Testa a função
        company_info = self.api.get_company(12345)
        
        self.assertIsNotNone(company_info)
        self.assertEqual(company_info['name'], 'Test Company')
        self.assertEqual(company_info['industry'], 'Technology')
        self.assertEqual(company_info['employeeCount'], 1000)

class TestTikTokAPI(unittest.TestCase):
    """Testes para a API do TikTok"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        with patch('modules.cache_manager.CacheManager'):
            self.api = TikTokAPI()
    
    @patch.object(TikTokAPI, '_make_request')
    def test_get_user_info_success(self, mock_make_request):
        """Testa obtenção bem-sucedida de informações do usuário"""
        # Mock da resposta da API
        mock_make_request.return_value = {
            "username": "test_user",
            "followers": 10000,
            "following": 500,
            "videos": 100,
            "bio": "Test bio"
        }
        
        # Testa a função
        user_info = self.api.get_user_info('test_user')
        
        # Verifica os resultados
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['username'], 'test_user')
        self.assertEqual(user_info['followers'], 10000)
        self.assertEqual(user_info['following'], 500)
        self.assertEqual(user_info['videos'], 100)
    
    @patch.object(TikTokAPI, '_make_request')
    def test_get_user_info_not_found(self, mock_make_request):
        """Testa comportamento quando usuário não é encontrado"""
        # Mock da resposta de erro
        mock_make_request.side_effect = Exception("Usuário não encontrado")
        
        # Testa a função
        with self.assertRaises(Exception):
            self.api.get_user_info('nonexistent_user')
    
    @patch.object(TikTokAPI, '_make_request')
    def test_get_video_info_success(self, mock_make_request):
        """Testa obtenção bem-sucedida de informações do vídeo"""
        # Mock da resposta da API
        mock_make_request.return_value = {
            "id": "123456789",
            "description": "Test video description",
            "likes": 1000,
            "shares": 100,
            "comments": 50,
            "views": 10000
        }
        
        # Testa a função
        video_info = self.api.get_video_info('123456789')
        
        # Verifica os resultados
        self.assertIsNotNone(video_info)
        self.assertEqual(video_info['id'], '123456789')
        self.assertEqual(video_info['description'], 'Test video description')
        self.assertEqual(video_info['likes'], 1000)
        self.assertEqual(video_info['shares'], 100)
        self.assertEqual(video_info['comments'], 50)
        self.assertEqual(video_info['views'], 10000)

class TestAPIIntegration(unittest.TestCase):
    """Testes de integração entre as APIs"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        with patch('modules.cache_manager.CacheManager') as mock_cache:
            # Configura o mock do cache para retornar None por padrão
            mock_cache.get.return_value = None
            mock_cache.set.return_value = None
            self.instagram_api = InstagramAPI('test_session_id', mock_cache)
            self.linkedin_api = LinkedInAPI(mock_cache)
            self.tiktok_api = TikTokAPI(mock_cache)
    
    def test_api_initialization(self):
        """Testa se todas as APIs são inicializadas corretamente"""
        self.assertIsNotNone(self.instagram_api)
        self.assertIsNotNone(self.linkedin_api)
        self.assertIsNotNone(self.tiktok_api)
        
        # Verifica se o cache manager foi inicializado
        self.assertIsNotNone(self.instagram_api.cache_manager)
        self.assertIsNotNone(self.linkedin_api.cache_manager)
        self.assertIsNotNone(self.tiktok_api.cache_manager)
    
    def test_error_handling(self):
        """Testa tratamento de erros nas APIs"""
        with patch('requests.get') as mock_get:
            # Simula erro de conexão (RequestException)
            mock_get.side_effect = requests.exceptions.RequestException("Connection error")
            
            # Testa se a API trata o erro graciosamente
            result = self.instagram_api.get_user_id('test_user')
            self.assertIsNotNone(result)
            self.assertIn('error', result)
            self.assertIsNone(result['id'])
            self.assertIn('Erro de rede', result['error'])
    
    def test_rate_limiting(self):
        """Testa comportamento com rate limiting"""
        with patch('requests.get') as mock_get:
            # Simula resposta de rate limiting
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_get.return_value = mock_response
            
            # Testa se a API trata o rate limiting
            result = self.instagram_api.get_user_id('test_user')
            self.assertIsNotNone(result)
            self.assertIn('error', result)
            self.assertEqual(result['error'], 'Rate limit atingido')

if __name__ == '__main__':
    unittest.main()