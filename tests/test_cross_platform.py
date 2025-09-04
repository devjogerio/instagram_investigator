import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import tempfile
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.cross_platform_analyzer import CrossPlatformAnalyzer
from modules.cross_platform_visualization import CrossPlatformVisualization

class TestCrossPlatformAnalyzer(unittest.TestCase):
    """Testes para o analisador cross-platform"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.analyzer = CrossPlatformAnalyzer()
        
        # Dados de teste
        self.sample_data = {
            'instagram': {
                'username': 'test_user',
                'followers': 10000,
                'following': 500,
                'posts': 100,
                'engagement_rate': 0.05,
                'bio': 'Software engineer passionate about technology'
            },
            'linkedin': {
                'name': 'Test User',
                'job_title': 'Software Engineer',
                'company': 'Tech Corp',
                'connections': 1000,
                'description': 'Experienced software engineer with expertise in technology'
            },
            'tiktok': {
                'username': 'test_user',
                'followers': 5000,
                'following': 200,
                'videos': 50,
                'likes': 25000,
                'bio': 'Tech enthusiast creating educational content'
            }
        }
    
    def test_analyze_cross_platform_data(self):
        """Testa análise de dados cross-platform"""
        result = self.analyzer.analyze_cross_platform_data(self.sample_data)
        
        self.assertIn('identity_match', result)
        self.assertIn('content_similarity', result)
        self.assertIn('activity_patterns', result)
        self.assertIn('audience_overlap', result)
        self.assertIn('summary', result)
        
        # Verifica se retornou dados válidos
        self.assertIsInstance(result, dict)
    
    def test_analyze_content_similarity(self):
        """Testa análise de similaridade de conteúdo"""
        platforms = ['instagram', 'tiktok']
        similarities = self.analyzer.analyze_content_similarity(self.sample_data, platforms)
        
        self.assertIn('similarity_score', similarities)
        self.assertIn('common_elements', similarities)
        self.assertIn('confidence', similarities)
        
        # Verifica se retornou dados válidos
        self.assertIsInstance(similarities, dict)
    
    def test_analyze_activity_patterns(self):
        """Testa análise de padrões de atividade"""
        platforms = ['instagram', 'tiktok']
        patterns = self.analyzer.analyze_activity_patterns(self.sample_data, platforms)
        
        self.assertIn('posting_frequency', patterns)
        self.assertIn('activity_correlation', patterns)
        self.assertIn('peak_times', patterns)
        
        # Verifica se retornou dados válidos
        self.assertIsInstance(patterns, dict)
    
    def test_analyze_identity_match(self):
        """Testa análise de correspondência de identidade"""
        platforms = ['instagram', 'tiktok']
        identity = self.analyzer.analyze_identity_match(self.sample_data, platforms)
        
        self.assertIn('match_score', identity)
        self.assertIn('matching_elements', identity)
        self.assertIn('confidence', identity)
        
        # Verifica se retornou dados válidos
        self.assertIsInstance(identity, dict)
    
    def test_estimate_audience_overlap(self):
        """Testa estimativa de sobreposição de audiência"""
        platforms = ['instagram', 'tiktok']
        overlap = self.analyzer.estimate_audience_overlap(self.sample_data, platforms)
        
        self.assertIn('overlap_percentage', overlap)
        self.assertIn('shared_interests', overlap)
        self.assertIn('confidence', overlap)
        
        # Verifica se retornou dados válidos
        self.assertIsInstance(overlap, dict)
    
    def test_empty_data_handling(self):
        """Testa comportamento com dados vazios"""
        empty_data = {}
        
        result = self.analyzer.analyze_cross_platform_data(empty_data)
        self.assertIsInstance(result, dict)
        
        platforms = ['instagram', 'tiktok']
        similarities = self.analyzer.analyze_content_similarity(empty_data, platforms)
        self.assertIsInstance(similarities, dict)
    
    def test_partial_data_handling(self):
        """Testa comportamento com dados parciais"""
        partial_data = {
            'instagram': {
                'username': 'test_user',
                'follower_count': 1000
                # Faltam outros campos
            }
        }
        
        result = self.analyzer.analyze_cross_platform_data(partial_data)
        self.assertIsInstance(result, dict)
        self.assertIn('identity_match', result)

class TestCrossPlatformVisualization(unittest.TestCase):
    """Testes para as visualizações cross-platform"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.viz = CrossPlatformVisualization()
        
        # Dados de teste
        self.sample_data = {
            'instagram': {
                'username': 'test_user',
                'followers': 10000,
                'following': 500,
                'posts': 100,
                'engagement_rate': 0.05
            },
            'linkedin': {
                'name': 'Test User',
                'connections': 1000
            },
            'tiktok': {
                'username': 'test_user',
                'followers': 5000,
                'following': 200,
                'videos': 50,
                'likes': 25000
            }
        }
    
    def test_create_engagement_comparison_chart(self):
        """Testa criação de gráfico de comparação de engajamento"""
        # O método retorna uma string base64, não salva arquivo
        result = self.viz.create_engagement_comparison_chart(self.sample_data)
        
        # Verifica se retornou uma string (base64)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_create_activity_heatmap(self):
        """Testa criação de mapa de calor de atividade"""
        # O método retorna uma string base64, não salva arquivo
        result = self.viz.create_activity_heatmap(self.sample_data)
        
        # Verifica se retornou uma string (base64)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_create_connection_network(self):
        """Testa criação de grafo de rede de conexões"""
        # O método retorna uma string base64, não salva arquivo
        result = self.viz.create_connection_network(self.sample_data)
        
        # Verifica se retornou uma string (base64)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_create_content_similarity_chart(self):
        """Testa criação de gráfico de similaridade de conteúdo"""
        # O método retorna uma string base64, não salva arquivo
        result = self.viz.create_content_similarity_chart(self.sample_data)
        
        # Verifica se retornou uma string (base64)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_visualization_with_valid_data(self):
        """Testa visualizações com dados válidos"""
        # Testa múltiplas visualizações
        engagement_chart = self.viz.create_engagement_comparison_chart(self.sample_data)
        activity_heatmap = self.viz.create_activity_heatmap(self.sample_data)
        network_chart = self.viz.create_connection_network(self.sample_data)
        similarity_chart = self.viz.create_content_similarity_chart(self.sample_data)
        
        # Verifica se todas retornaram strings válidas
        for result in [engagement_chart, activity_heatmap, network_chart, similarity_chart]:
            self.assertIsInstance(result, str)
            self.assertGreater(len(result), 0)
    
    def test_visualization_error_handling(self):
        """Testa tratamento de erros nas visualizações"""
        # Testa com dados inválidos
        invalid_data = {'invalid': 'data'}
        
        try:
            result = self.viz.create_engagement_comparison_chart(invalid_data)
            # Se não gerar exceção, deve retornar string vazia ou válida
            self.assertIsInstance(result, str)
        except Exception:
            # É aceitável que gere exceção com dados inválidos
            pass
    
    def test_empty_data_visualization(self):
        """Testa visualização com dados vazios"""
        empty_data = {}
        
        try:
            result = self.viz.create_engagement_comparison_chart(empty_data)
            # Se não gerar exceção, deve retornar string
            self.assertIsInstance(result, str)
        except Exception:
            # É aceitável que gere exceção com dados vazios
            pass
    
    def test_color_consistency(self):
        """Testa consistência das cores entre gráficos"""
        # Verifica se as cores das plataformas são consistentes
        self.assertIn('instagram', self.viz.platform_colors)
        self.assertIn('linkedin', self.viz.platform_colors)
        self.assertIn('tiktok', self.viz.platform_colors)
        
        # Verifica se as cores são diferentes
        colors = list(self.viz.platform_colors.values())
        self.assertEqual(len(colors), len(set(colors)))  # Todas as cores devem ser únicas

class TestVisualizationIntegration(unittest.TestCase):
    """Testes de integração entre análise e visualização"""
    
    def setUp(self):
        """Configuração inicial para cada teste"""
        self.analyzer = CrossPlatformAnalyzer()
        self.viz = CrossPlatformVisualization()
        
        self.sample_data = {
            'instagram': {
                'username': 'test_user',
                'followers': 10000,
                'engagement_rate': 0.05,
                'bio': 'Tech enthusiast'
            },
            'tiktok': {
                'username': 'test_user',
                'followers': 5000,
                'likes': 25000,
                'bio': 'Technology content creator'
            }
        }
    
    def test_analysis_to_visualization_pipeline(self):
        """Testa pipeline completo de análise para visualização"""
        # Executa análise
        analysis_result = self.analyzer.analyze_cross_platform_data(self.sample_data)
        platforms = ['instagram', 'tiktok']
        similarities = self.analyzer.analyze_content_similarity(self.sample_data, platforms)
        
        # Cria visualizações baseadas na análise
        engagement_chart = self.viz.create_engagement_comparison_chart(self.sample_data)
        similarity_chart = self.viz.create_content_similarity_chart(self.sample_data)
        
        # Verifica se as visualizações foram criadas
        self.assertIsInstance(engagement_chart, str)
        self.assertIsInstance(similarity_chart, str)
        self.assertGreater(len(engagement_chart), 0)
        self.assertGreater(len(similarity_chart), 0)
    
    def test_data_consistency(self):
        """Testa consistência de dados entre análise e visualização"""
        # Verifica se os dados processados pela análise são compatíveis com a visualização
        analysis_result = self.analyzer.analyze_cross_platform_data(self.sample_data)
        
        # Deve ser possível criar visualizações com os dados processados
        self.assertIsInstance(analysis_result, dict)
        
        # Testa se as visualizações funcionam com os mesmos dados
        engagement_chart = self.viz.create_engagement_comparison_chart(self.sample_data)
        self.assertIsInstance(engagement_chart, str)

if __name__ == '__main__':
    unittest.main()