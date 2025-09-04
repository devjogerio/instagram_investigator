#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para visualização de dados do Instagram
Gera gráficos e visualizações para análise dos dados coletados
"""

import matplotlib.pyplot as plt
import matplotlib
import io
import base64
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Configuração para usar o backend Agg (não interativo) do matplotlib
matplotlib.use('Agg')

class DataVisualization:
    """Classe para geração de gráficos e visualizações dos dados coletados"""
    
    def __init__(self):
        """Inicializa o módulo de visualização"""
        # Configuração de estilo para os gráficos
        plt.style.use('ggplot')
        self.colors = ['#E1306C', '#833AB4', '#405DE6', '#5851DB']
    
    def generate_engagement_chart(self, user_data):
        """Gera gráfico de engajamento (likes e comentários)"""
        try:
            # Extrai dados de engajamento
            media_count = user_data.get('media_count', 0)
            followers = user_data.get('follower_count', 0)
            following = user_data.get('following_count', 0)
            
            if media_count == 0 or followers == 0:
                logger.warning("Dados insuficientes para gerar gráfico de engajamento")
                return None
            
            # Calcula taxa de engajamento estimada
            engagement_rate = (followers / (media_count * 100)) if media_count > 0 else 0
            
            # Cria figura
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Dados para o gráfico
            metrics = ['Seguidores', 'Seguindo', 'Posts', 'Taxa de Engajamento x100']
            values = [followers, following, media_count, engagement_rate]
            
            # Cria barras
            bars = ax.bar(metrics, values, color=self.colors)
            
            # Adiciona valores no topo das barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height):,}' if height > 1 else f'{height:.2f}',
                        ha='center', va='bottom', fontsize=9)
            
            # Configurações do gráfico
            ax.set_title('Métricas de Engajamento', fontsize=14)
            ax.set_ylabel('Quantidade')
            plt.xticks(rotation=0)
            plt.tight_layout()
            
            # Converte o gráfico para base64
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de engajamento: {str(e)}")
            return None
    
    def generate_activity_chart(self, user_data):
        """Gera gráfico de atividade recente"""
        try:
            # Extrai dados de atividade
            media_count = user_data.get('media_count', 0)
            last_post_timestamp = user_data.get('last_post_timestamp')
            account_created = user_data.get('account_created')
            
            if not last_post_timestamp or not account_created:
                logger.warning("Dados insuficientes para gerar gráfico de atividade")
                return None
            
            # Converte timestamps para datetime
            try:
                last_post_date = datetime.fromtimestamp(last_post_timestamp)
                account_created_date = datetime.fromtimestamp(account_created)
            except:
                logger.warning("Erro ao converter timestamps")
                return None
            
            # Calcula dias desde a criação da conta e último post
            now = datetime.now()
            days_since_creation = (now - account_created_date).days
            days_since_last_post = (now - last_post_date).days
            
            # Calcula média de posts por mês
            months_active = max(days_since_creation / 30, 1)  # Evita divisão por zero
            posts_per_month = media_count / months_active
            
            # Cria figura
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Dados para o gráfico
            metrics = ['Dias desde criação', 'Dias desde último post', 'Posts por mês']
            values = [days_since_creation, days_since_last_post, posts_per_month]
            
            # Cria barras
            bars = ax.bar(metrics, values, color=self.colors)
            
            # Adiciona valores no topo das barras
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height):,}' if height > 1 else f'{height:.2f}',
                        ha='center', va='bottom', fontsize=9)
            
            # Configurações do gráfico
            ax.set_title('Métricas de Atividade', fontsize=14)
            ax.set_ylabel('Dias / Quantidade')
            plt.xticks(rotation=15)
            plt.tight_layout()
            
            # Converte o gráfico para base64
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de atividade: {str(e)}")
            return None
    
    def generate_profile_summary(self, user_data):
        """Gera gráfico de resumo do perfil"""
        try:
            # Extrai dados do perfil
            is_private = user_data.get('is_private', False)
            is_verified = user_data.get('is_verified', False)
            has_bio = bool(user_data.get('biography', ''))
            has_external_url = bool(user_data.get('external_url', ''))
            has_profile_pic = user_data.get('has_profile_pic', False)
            
            # Cria figura
            fig, ax = plt.subplots(figsize=(8, 5))
            
            # Dados para o gráfico
            metrics = ['Privado', 'Verificado', 'Bio', 'URL Externa', 'Foto de Perfil']
            values = [int(is_private), int(is_verified), int(has_bio), int(has_external_url), int(has_profile_pic)]
            
            # Cria barras
            bars = ax.bar(metrics, values, color=self.colors)
            
            # Adiciona valores no topo das barras (Sim/Não)
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                        'Sim' if height > 0 else 'Não',
                        ha='center', va='bottom', fontsize=9)
            
            # Configurações do gráfico
            ax.set_title('Características do Perfil', fontsize=14)
            ax.set_ylim(0, 1.2)  # Limita o eixo Y para valores binários
            plt.xticks(rotation=15)
            plt.tight_layout()
            
            # Converte o gráfico para base64
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Erro ao gerar gráfico de resumo do perfil: {str(e)}")
            return None
    
    def _fig_to_base64(self, fig):
        """Converte uma figura matplotlib para string base64"""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100)
        plt.close(fig)  # Fecha a figura para liberar memória
        buf.seek(0)
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        return img_str