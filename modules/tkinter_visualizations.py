#!/usr/bin/env python3
"""
Módulo de Visualizações para Tkinter
Substitui as visualizações baseadas em Flet por implementações Tkinter com matplotlib
"""

import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import io
import base64
from datetime import datetime, timedelta

class TkinterVisualizationManager:
    """
    Gerenciador de visualizações para interface Tkinter
    """
    
    def __init__(self):
        """
        Inicializa o gerenciador de visualizações
        """
        # Configurar estilo do matplotlib
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Cores do tema
        self.colors = {
            'primary': '#1565C0',
            'secondary': '#1976D2', 
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'info': '#2196F3'
        }
        
        # Configurações padrão
        self.default_figsize = (10, 6)
        self.default_dpi = 100
    
    def create_engagement_comparison_chart(self, parent: tk.Widget, platform_data: Dict[str, Any]) -> tk.Widget:
        """
        Cria gráfico de comparação de engajamento entre plataformas
        
        Args:
            parent: Widget pai
            platform_data: Dados das plataformas
            
        Returns:
            Frame contendo o gráfico
        """
        # Criar frame para o gráfico
        chart_frame = ttk.LabelFrame(parent, text="📊 Comparação de Engajamento", padding="10")
        
        try:
            # Preparar dados
            platforms = []
            followers = []
            following = []
            posts = []
            
            for platform, data in platform_data.items():
                if isinstance(data, dict):
                    platforms.append(platform.capitalize())
                    followers.append(data.get('followers_count', 0))
                    following.append(data.get('following_count', 0))
                    posts.append(data.get('posts_count', 0))
            
            if not platforms:
                # Exibir mensagem se não houver dados
                ttk.Label(chart_frame, text="Nenhum dado disponível para visualização",
                         font=('Segoe UI', 12)).pack(pady=20)
                return chart_frame
            
            # Criar figura
            fig = Figure(figsize=self.default_figsize, dpi=self.default_dpi)
            
            # Subplot para seguidores
            ax1 = fig.add_subplot(2, 2, 1)
            bars1 = ax1.bar(platforms, followers, color=self.colors['primary'], alpha=0.7)
            ax1.set_title('Seguidores por Plataforma')
            ax1.set_ylabel('Número de Seguidores')
            
            # Adicionar valores nas barras
            for bar, value in zip(bars1, followers):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:,}', ha='center', va='bottom')
            
            # Subplot para seguindo
            ax2 = fig.add_subplot(2, 2, 2)
            bars2 = ax2.bar(platforms, following, color=self.colors['secondary'], alpha=0.7)
            ax2.set_title('Seguindo por Plataforma')
            ax2.set_ylabel('Número Seguindo')
            
            for bar, value in zip(bars2, following):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:,}', ha='center', va='bottom')
            
            # Subplot para posts
            ax3 = fig.add_subplot(2, 2, 3)
            bars3 = ax3.bar(platforms, posts, color=self.colors['success'], alpha=0.7)
            ax3.set_title('Posts por Plataforma')
            ax3.set_ylabel('Número de Posts')
            
            for bar, value in zip(bars3, posts):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:,}', ha='center', va='bottom')
            
            # Subplot para taxa de engajamento (followers/following ratio)
            ax4 = fig.add_subplot(2, 2, 4)
            engagement_ratios = [f/max(fo, 1) for f, fo in zip(followers, following)]
            bars4 = ax4.bar(platforms, engagement_ratios, color=self.colors['warning'], alpha=0.7)
            ax4.set_title('Taxa de Engajamento (Seguidores/Seguindo)')
            ax4.set_ylabel('Ratio')
            
            for bar, value in zip(bars4, engagement_ratios):
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{value:.2f}', ha='center', va='bottom')
            
            # Ajustar layout
            fig.tight_layout()
            
            # Criar canvas
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Toolbar de navegação
            toolbar = NavigationToolbar2Tk(canvas, chart_frame)
            toolbar.update()
            
        except Exception as e:
            # Exibir erro se houver problema
            error_label = ttk.Label(chart_frame, 
                                  text=f"Erro ao gerar gráfico: {str(e)}",
                                  foreground='red')
            error_label.pack(pady=20)
        
        return chart_frame
    
    def create_growth_metrics_chart(self, parent: tk.Widget, platform_data: Dict[str, Any]) -> tk.Widget:
        """
        Cria gráfico de métricas de crescimento
        
        Args:
            parent: Widget pai
            platform_data: Dados das plataformas
            
        Returns:
            Frame contendo o gráfico
        """
        chart_frame = ttk.LabelFrame(parent, text="📈 Métricas de Crescimento", padding="10")
        
        try:
            # Preparar dados simulados de crescimento (em um cenário real, viriam da API)
            platforms = list(platform_data.keys())
            
            if not platforms:
                ttk.Label(chart_frame, text="Nenhum dado disponível para visualização",
                         font=('Segoe UI', 12)).pack(pady=20)
                return chart_frame
            
            # Gerar dados simulados de crescimento dos últimos 30 dias
            dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
            
            fig = Figure(figsize=self.default_figsize, dpi=self.default_dpi)
            ax = fig.add_subplot(1, 1, 1)
            
            colors = [self.colors['primary'], self.colors['secondary'], 
                     self.colors['success'], self.colors['warning'], self.colors['info']]
            
            for i, platform in enumerate(platforms[:5]):  # Máximo 5 plataformas
                # Simular crescimento baseado nos dados atuais
                current_followers = platform_data[platform].get('followers_count', 1000)
                base_growth = max(1, current_followers // 1000)  # Taxa base de crescimento
                
                # Gerar série temporal simulada
                growth_data = []
                for day in range(30):
                    # Variação aleatória no crescimento
                    daily_growth = np.random.normal(base_growth, base_growth * 0.1)
                    growth_data.append(max(0, daily_growth))
                
                # Criar série cumulativa
                cumulative_growth = np.cumsum(growth_data)
                
                ax.plot(dates, cumulative_growth, 
                       label=platform.capitalize(), 
                       color=colors[i % len(colors)],
                       linewidth=2, marker='o', markersize=4)
            
            ax.set_title('Crescimento de Seguidores (Últimos 30 dias)', fontsize=14, fontweight='bold')
            ax.set_xlabel('Data')
            ax.set_ylabel('Novos Seguidores')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Formatar eixo x
            fig.autofmt_xdate()
            
            # Ajustar layout
            fig.tight_layout()
            
            # Criar canvas
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Toolbar
            toolbar = NavigationToolbar2Tk(canvas, chart_frame)
            toolbar.update()
            
        except Exception as e:
            error_label = ttk.Label(chart_frame, 
                                  text=f"Erro ao gerar gráfico: {str(e)}",
                                  foreground='red')
            error_label.pack(pady=20)
        
        return chart_frame
    
    def create_content_distribution_chart(self, parent: tk.Widget, platform_data: Dict[str, Any]) -> tk.Widget:
        """
        Cria gráfico de distribuição de tipos de conteúdo
        
        Args:
            parent: Widget pai
            platform_data: Dados das plataformas
            
        Returns:
            Frame contendo o gráfico
        """
        chart_frame = ttk.LabelFrame(parent, text="🎯 Distribuição de Conteúdo", padding="10")
        
        try:
            # Simular dados de tipos de conteúdo
            content_types = ['Fotos', 'Vídeos', 'Stories', 'Reels', 'IGTV']
            
            fig = Figure(figsize=self.default_figsize, dpi=self.default_dpi)
            
            # Criar subplots para cada plataforma
            num_platforms = len(platform_data)
            if num_platforms == 0:
                ttk.Label(chart_frame, text="Nenhum dado disponível para visualização",
                         font=('Segoe UI', 12)).pack(pady=20)
                return chart_frame
            
            cols = min(2, num_platforms)
            rows = (num_platforms + cols - 1) // cols
            
            for i, (platform, data) in enumerate(platform_data.items()):
                ax = fig.add_subplot(rows, cols, i + 1)
                
                # Simular distribuição baseada no número de posts
                total_posts = data.get('posts_count', 100)
                
                # Distribuição simulada
                if platform.lower() == 'instagram':
                    distribution = [0.4, 0.25, 0.15, 0.15, 0.05]  # Instagram típico
                elif platform.lower() == 'facebook':
                    distribution = [0.5, 0.3, 0.1, 0.05, 0.05]  # Facebook típico
                else:
                    distribution = [0.3, 0.3, 0.2, 0.1, 0.1]  # Distribuição genérica
                
                # Calcular valores absolutos
                values = [int(total_posts * dist) for dist in distribution]
                
                # Criar gráfico de pizza
                colors_pie = plt.cm.Set3(np.linspace(0, 1, len(content_types)))
                wedges, texts, autotexts = ax.pie(values, labels=content_types, 
                                                 autopct='%1.1f%%', colors=colors_pie)
                
                ax.set_title(f'{platform.capitalize()}', fontweight='bold')
                
                # Melhorar legibilidade
                for autotext in autotexts:
                    autotext.set_color('white')
                    autotext.set_fontweight('bold')
            
            # Ajustar layout
            fig.tight_layout()
            
            # Criar canvas
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Toolbar
            toolbar = NavigationToolbar2Tk(canvas, chart_frame)
            toolbar.update()
            
        except Exception as e:
            error_label = ttk.Label(chart_frame, 
                                  text=f"Erro ao gerar gráfico: {str(e)}",
                                  foreground='red')
            error_label.pack(pady=20)
        
        return chart_frame
    
    def create_sentiment_analysis_chart(self, parent: tk.Widget, platform_data: Dict[str, Any]) -> tk.Widget:
        """
        Cria gráfico de análise de sentimentos
        
        Args:
            parent: Widget pai
            platform_data: Dados das plataformas
            
        Returns:
            Frame contendo o gráfico
        """
        chart_frame = ttk.LabelFrame(parent, text="😊 Análise de Sentimentos", padding="10")
        
        try:
            platforms = list(platform_data.keys())
            
            if not platforms:
                ttk.Label(chart_frame, text="Nenhum dado disponível para visualização",
                         font=('Segoe UI', 12)).pack(pady=20)
                return chart_frame
            
            # Simular dados de sentimento
            sentiments = ['Positivo', 'Neutro', 'Negativo']
            sentiment_colors = [self.colors['success'], '#FFC107', self.colors['error']]
            
            fig = Figure(figsize=self.default_figsize, dpi=self.default_dpi)
            ax = fig.add_subplot(1, 1, 1)
            
            # Dados simulados para cada plataforma
            x = np.arange(len(platforms))
            width = 0.25
            
            positive_scores = []
            neutral_scores = []
            negative_scores = []
            
            for platform in platforms:
                # Simular scores baseados na plataforma
                if platform.lower() == 'instagram':
                    pos, neu, neg = 0.6, 0.3, 0.1
                elif platform.lower() == 'facebook':
                    pos, neu, neg = 0.5, 0.35, 0.15
                else:
                    pos, neu, neg = 0.55, 0.3, 0.15
                
                # Adicionar variação aleatória
                variation = np.random.normal(0, 0.05)
                pos = max(0.1, min(0.9, pos + variation))
                neg = max(0.05, min(0.3, neg - variation/2))
                neu = 1 - pos - neg
                
                positive_scores.append(pos)
                neutral_scores.append(neu)
                negative_scores.append(neg)
            
            # Criar barras agrupadas
            bars1 = ax.bar(x - width, positive_scores, width, label='Positivo', 
                          color=sentiment_colors[0], alpha=0.8)
            bars2 = ax.bar(x, neutral_scores, width, label='Neutro', 
                          color=sentiment_colors[1], alpha=0.8)
            bars3 = ax.bar(x + width, negative_scores, width, label='Negativo', 
                          color=sentiment_colors[2], alpha=0.8)
            
            # Configurar gráfico
            ax.set_title('Análise de Sentimentos por Plataforma', fontsize=14, fontweight='bold')
            ax.set_ylabel('Proporção')
            ax.set_xlabel('Plataformas')
            ax.set_xticks(x)
            ax.set_xticklabels([p.capitalize() for p in platforms])
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            # Adicionar valores nas barras
            def add_value_labels(bars, values):
                for bar, value in zip(bars, values):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                           f'{value:.1%}', ha='center', va='bottom', fontsize=9)
            
            add_value_labels(bars1, positive_scores)
            add_value_labels(bars2, neutral_scores)
            add_value_labels(bars3, negative_scores)
            
            # Ajustar layout
            fig.tight_layout()
            
            # Criar canvas
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Toolbar
            toolbar = NavigationToolbar2Tk(canvas, chart_frame)
            toolbar.update()
            
        except Exception as e:
            error_label = ttk.Label(chart_frame, 
                                  text=f"Erro ao gerar gráfico: {str(e)}",
                                  foreground='red')
            error_label.pack(pady=20)
        
        return chart_frame
    
    def create_activity_heatmap(self, parent: tk.Widget, platform_data: Dict[str, Any]) -> tk.Widget:
        """
        Cria mapa de calor de atividade
        
        Args:
            parent: Widget pai
            platform_data: Dados das plataformas
            
        Returns:
            Frame contendo o gráfico
        """
        chart_frame = ttk.LabelFrame(parent, text="🔥 Mapa de Calor de Atividade", padding="10")
        
        try:
            if not platform_data:
                ttk.Label(chart_frame, text="Nenhum dado disponível para visualização",
                         font=('Segoe UI', 12)).pack(pady=20)
                return chart_frame
            
            # Simular dados de atividade por hora e dia da semana
            days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
            hours = list(range(24))
            
            # Gerar matriz de atividade simulada
            activity_matrix = np.random.rand(7, 24) * 100
            
            # Adicionar padrões realistas
            for day in range(7):
                for hour in range(24):
                    # Menor atividade durante a madrugada
                    if 0 <= hour <= 6:
                        activity_matrix[day, hour] *= 0.3
                    # Maior atividade durante horários comerciais
                    elif 9 <= hour <= 17:
                        activity_matrix[day, hour] *= 1.5
                    # Atividade moderada à noite
                    elif 18 <= hour <= 23:
                        activity_matrix[day, hour] *= 1.2
            
            fig = Figure(figsize=(12, 6), dpi=self.default_dpi)
            ax = fig.add_subplot(1, 1, 1)
            
            # Criar heatmap
            im = ax.imshow(activity_matrix, cmap='YlOrRd', aspect='auto')
            
            # Configurar eixos
            ax.set_xticks(range(24))
            ax.set_xticklabels([f'{h:02d}:00' for h in hours], rotation=45)
            ax.set_yticks(range(7))
            ax.set_yticklabels(days)
            
            # Título e rótulos
            ax.set_title('Mapa de Calor de Atividade (Posts por Hora/Dia)', 
                        fontsize=14, fontweight='bold')
            ax.set_xlabel('Hora do Dia')
            ax.set_ylabel('Dia da Semana')
            
            # Colorbar
            cbar = fig.colorbar(im, ax=ax)
            cbar.set_label('Número de Posts', rotation=270, labelpad=20)
            
            # Adicionar valores nas células
            for i in range(7):
                for j in range(24):
                    value = activity_matrix[i, j]
                    color = 'white' if value > 50 else 'black'
                    ax.text(j, i, f'{value:.0f}', ha='center', va='center', 
                           color=color, fontsize=8)
            
            # Ajustar layout
            fig.tight_layout()
            
            # Criar canvas
            canvas = FigureCanvasTkAgg(fig, chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
            # Toolbar
            toolbar = NavigationToolbar2Tk(canvas, chart_frame)
            toolbar.update()
            
        except Exception as e:
            error_label = ttk.Label(chart_frame, 
                                  text=f"Erro ao gerar gráfico: {str(e)}",
                                  foreground='red')
            error_label.pack(pady=20)
        
        return chart_frame
    
    def create_comprehensive_dashboard(self, parent: tk.Widget, platform_data: Dict[str, Any],
                                     analysis_data: Dict[str, Any] = None) -> tk.Widget:
        """
        Cria um dashboard abrangente com múltiplas visualizações
        
        Args:
            parent: Widget pai
            platform_data: Dados das plataformas
            analysis_data: Dados de análise cruzada
            
        Returns:
            Frame contendo o dashboard
        """
        dashboard_frame = ttk.Frame(parent)
        
        # Criar notebook para organizar visualizações
        viz_notebook = ttk.Notebook(dashboard_frame)
        viz_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Aba 1: Comparação de Engajamento
        engagement_frame = ttk.Frame(viz_notebook)
        viz_notebook.add(engagement_frame, text="📊 Engajamento")
        engagement_chart = self.create_engagement_comparison_chart(engagement_frame, platform_data)
        engagement_chart.pack(fill=tk.BOTH, expand=True)
        
        # Aba 2: Métricas de Crescimento
        growth_frame = ttk.Frame(viz_notebook)
        viz_notebook.add(growth_frame, text="📈 Crescimento")
        growth_chart = self.create_growth_metrics_chart(growth_frame, platform_data)
        growth_chart.pack(fill=tk.BOTH, expand=True)
        
        # Aba 3: Distribuição de Conteúdo
        content_frame = ttk.Frame(viz_notebook)
        viz_notebook.add(content_frame, text="🎯 Conteúdo")
        content_chart = self.create_content_distribution_chart(content_frame, platform_data)
        content_chart.pack(fill=tk.BOTH, expand=True)
        
        # Aba 4: Análise de Sentimentos
        sentiment_frame = ttk.Frame(viz_notebook)
        viz_notebook.add(sentiment_frame, text="😊 Sentimentos")
        sentiment_chart = self.create_sentiment_analysis_chart(sentiment_frame, platform_data)
        sentiment_chart.pack(fill=tk.BOTH, expand=True)
        
        # Aba 5: Mapa de Calor
        heatmap_frame = ttk.Frame(viz_notebook)
        viz_notebook.add(heatmap_frame, text="🔥 Atividade")
        heatmap_chart = self.create_activity_heatmap(heatmap_frame, platform_data)
        heatmap_chart.pack(fill=tk.BOTH, expand=True)
        
        return dashboard_frame
    
    def export_chart_as_image(self, figure: Figure, filename: str, format: str = 'png') -> str:
        """
        Exporta um gráfico como imagem
        
        Args:
            figure: Figura matplotlib
            filename: Nome do arquivo
            format: Formato da imagem ('png', 'jpg', 'svg', 'pdf')
            
        Returns:
            Caminho do arquivo salvo
        """
        try:
            filepath = f"{filename}.{format}"
            figure.savefig(filepath, format=format, dpi=300, bbox_inches='tight')
            return filepath
        except Exception as e:
            print(f"Erro ao exportar gráfico: {str(e)}")
            return ""
    
    def get_chart_as_base64(self, figure: Figure) -> str:
        """
        Converte um gráfico para string base64
        
        Args:
            figure: Figura matplotlib
            
        Returns:
            String base64 da imagem
        """
        try:
            buffer = io.BytesIO()
            figure.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
            buffer.close()
            return image_base64
        except Exception as e:
            print(f"Erro ao converter gráfico para base64: {str(e)}")
            return ""