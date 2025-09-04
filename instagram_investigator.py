#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicação de Extração de Dados de Redes Sociais
Desenvolvido com base no script OSINT original de Bruno Fraga (@brunofragax)
Adaptado para interface gráfica com Flet e suporte a múltiplas plataformas
"""

import flet as ft
import os
import sys
import json
import csv
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional

# Importa os módulos da aplicação
from modules.instagram_api import InstagramAPI
from modules.data_extractor import DataExtractor
from modules.utils import Colors, setup_logger
from modules.cache_manager import CacheManager
from modules.data_visualization import DataVisualization
from modules.batch_processor import BatchProcessor

# Importa módulos para múltiplas plataformas
from modules.cross_platform_analyzer import CrossPlatformAnalyzer
from modules.cross_platform_visualization import CrossPlatformVisualization
from modules.multi_platform_ui import MultiPlatformUI
from modules.multi_platform_view import MultiPlatformView

# Importa módulos específicos de cada plataforma (se disponíveis)
try:
    from modules.facebook_api import FacebookAPI
    from modules.facebook_extractor import FacebookExtractor
    FACEBOOK_AVAILABLE = True
except ImportError:
    FACEBOOK_AVAILABLE = False

try:
    from modules.twitter_extractor import TwitterExtractor
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

try:
    from modules.linkedin_api import LinkedInAPI
    from modules.linkedin_extractor import LinkedInExtractor
    LINKEDIN_AVAILABLE = True
except ImportError:
    LINKEDIN_AVAILABLE = False

try:
    from modules.tiktok_api import TikTokAPI
    from modules.tiktok_extractor import TikTokExtractor
    TIKTOK_AVAILABLE = True
except ImportError:
    TIKTOK_AVAILABLE = False

# Carrega variáveis de ambiente
load_dotenv()

# Configura logger
logger = setup_logger()

# Configuração do cache
cache_duration = int(os.getenv('CACHE_DURATION', '3600'))  # Padrão: 1 hora
cache_manager = CacheManager(cache_duration=cache_duration)

# Inicializa o módulo de visualização de dados
data_viz = DataVisualization()

# Inicializa o processador em lote
batch_processor = None


class InstagramInvestigator:
    """Classe principal da aplicação"""
    
    def main(page: ft.Page):
        """Função principal da aplicação Flet"""
        # Configurações da página
        page.title = "Social Media Investigator"
        page.theme_mode = ft.ThemeMode.DARK
        page.window_width = 1200
        page.window_height = 800
        page.window_resizable = True
        page.padding = 20
        page.scroll = ft.ScrollMode.AUTO
        
        # Estado da aplicação
        page.session_data = {}
        page.current_platform = "instagram"  # Plataforma padrão
        
        # Inicializa componentes de UI para múltiplas plataformas
        multi_platform_ui = MultiPlatformUI(page)
        
        # Inicializa o gerenciador de cache
        cache_duration = int(os.getenv('CACHE_DURATION', 3600))  # Padrão: 1 hora
        cache_manager = CacheManager(cache_dir="cache", cache_duration=cache_duration)
        
        # Função para exibir mensagens de status
        def show_snackbar(message, color="success"):
            if color == "success":
                bgcolor = ft.Colors.GREEN
            elif color == "error":
                bgcolor = ft.Colors.RED_ACCENT
            else:
                bgcolor = ft.Colors.BLUE
                
            page.snack_bar = ft.SnackBar(
                content=ft.Text(message),
                bgcolor=bgcolor
            )
            page.snack_bar.open = True
            page.update()
        
        # Função para alternar entre as visualizações
        def change_view(e, view_name):
            content_container.content = views[view_name]
            
            # Atualiza estatísticas de cache se estiver indo para a visualização de cache
            if view_name == "cache":
                update_cache_stats()
                
            page.update()
            
        # Função para atualizar as estatísticas de cache
        def update_cache_stats():
            stats = cache_manager.get_stats()
            cache_stats_container.controls.clear()
            cache_stats_container.controls.extend([
                ft.Text(f"Total de arquivos em cache: {stats['total_files']}", size=16),
                ft.Text(f"Tamanho total: {stats['total_size_mb']} MB", size=16),
                ft.Text(f"Arquivos válidos: {stats['valid_files']}", size=16),
                ft.Text(f"Arquivos expirados: {stats['expired_files']}", size=16),
                ft.Text(f"Duração do cache: {cache_duration} segundos ({cache_duration // 60} minutos)", size=16),
            ])
            page.update()
            
        # Função para limpar o cache
        def clear_cache(e):
            count = cache_manager.clear()
            show_snackbar(f"Cache limpo: {count} arquivos removidos", "info")
            update_cache_stats()
            page.update()
        
        # Função para investigar perfil
        def investigate_profile(e):
            try:
                username = username_field.value.strip().lstrip('@')
                session_id = session_id_field.value.strip()
                
                if not username:
                    show_snackbar("Nome de usuário é obrigatório!", "error")
                    return
                    
                if not session_id:
                    show_snackbar("Session ID é obrigatório!", "error")
                    return
                
                # Atualiza interface para mostrar progresso
                progress_text.value = "Iniciando investigação..."
                progress_bar.visible = True
                page.update()
                
                # Cria instância do extrator de dados
                extractor = DataExtractor(session_id)
                
                # Inicia investigação
                progress_text.value = "Obtendo ID do usuário..."
                page.update()
                
                # Obtém dados do perfil
                profile_data = extractor.investigate_profile(username)
                
                # Armazena dados na sessão
                page.session_data = profile_data
                
                # Preenche os resultados na interface
                fill_results(profile_data)
                
                # Gera os gráficos para visualização
                generate_charts(profile_data)
                
                # Esconde barra de progresso e mostra resultados
                progress_bar.visible = False
                change_view(None, "results")
                show_snackbar(f"Investigação de @{username} concluída com sucesso!")
                
            except Exception as e:
                progress_bar.visible = False
                show_snackbar(f"Erro: {str(e)}", "error")
                page.update()
        
        # Função para preencher resultados do Instagram
        def fill_results(data):
            # Limpa resultados anteriores
            results_container.controls.clear()
            
        # Função para preencher resultados de múltiplas plataformas
        def fill_multi_platform_results(results):
            # Limpa resultados anteriores
            multi_platform_results_container.controls.clear()
            
            # Adiciona título
            multi_platform_results_container.controls.append(ft.Text(
                "RESULTADOS DE MÚLTIPLAS PLATAFORMAS",
                size=24,
                weight=ft.FontWeight.BOLD
            ))
            
            # Adiciona cards para cada plataforma
            platform_cards = ft.Row(wrap=True, spacing=20, alignment=ft.MainAxisAlignment.CENTER)
            
            for platform, data in results.items():
                if platform != "cross_platform" and platform != "cross_analysis":
                    platform_cards.controls.append(
                        multi_platform_ui.create_cross_platform_result_card(data, platform)
                    )
            
            multi_platform_results_container.controls.append(platform_cards)
            
            # Adiciona análise cruzada se disponível
            if "cross_analysis" in results:
                multi_platform_results_container.controls.append(ft.Text(
                    "ANÁLISE CRUZADA",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    margin=ft.margin.only(top=20)
                ))
                
                cross_analysis = results["cross_analysis"]
                
                # Correspondência de identidade
                if "identity_match" in cross_analysis:
                    multi_platform_results_container.controls.append(ft.Text(
                        "Correspondência de Identidade",
                        size=16,
                        weight=ft.FontWeight.BOLD
                    ))
                    
                    identity_info = ft.Column([
                        ft.Text(f"Nível de confiança: {cross_analysis['identity_match'].get('confidence_level', 'N/A')}%"),
                        ft.Text(f"Plataformas correspondentes: {', '.join(cross_analysis['identity_match'].get('matching_platforms', []))}"),
                    ])
                    multi_platform_results_container.controls.append(identity_info)
                
                # Similaridade de conteúdo
                if "content_similarity" in cross_analysis:
                    multi_platform_results_container.controls.append(ft.Text(
                        "Similaridade de Conteúdo",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        margin=ft.margin.only(top=10)
                    ))
                    
                    content_info = ft.Column([
                        ft.Text(f"Temas comuns: {', '.join(cross_analysis['content_similarity'].get('common_themes', []))}"),
                        ft.Text(f"Hashtags comuns: {', '.join(cross_analysis['content_similarity'].get('common_hashtags', []))}"),
                    ])
                    multi_platform_results_container.controls.append(content_info)
                
                # Padrões de atividade
                if "activity_patterns" in cross_analysis:
                    multi_platform_results_container.controls.append(ft.Text(
                        "Padrões de Atividade",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        margin=ft.margin.only(top=10)
                    ))
                    
                    activity_info = ft.Column([
                        ft.Text(f"Plataforma mais ativa: {cross_analysis['activity_patterns'].get('most_active_platform', 'N/A')}"),
                        ft.Text(f"Horários de pico: {', '.join(cross_analysis['activity_patterns'].get('peak_hours', []))}"),
                    ])
                    multi_platform_results_container.controls.append(activity_info)
            
            # Adiciona botões de ação
            multi_platform_results_container.controls.append(ft.Row([
                ft.ElevatedButton(
                    "Visualizar Gráficos Comparativos",
                    icon=ft.Icons.BAR_CHART,
                    on_click=lambda e: change_view(e, "cross_platform_charts")
                ),
                ft.ElevatedButton(
                    "Exportar Dados Combinados",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: change_view(e, "export")
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20))
            
            # Adiciona timestamp
            multi_platform_results_container.controls.append(ft.Text(
                f"Investigação concluída em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                italic=True,
                size=12,
                margin=ft.margin.only(top=20)
            ))
            
            page.update()
            
            # Adiciona informações básicas
            results_container.controls.append(ft.Text(
                "INFORMAÇÕES BÁSICAS",
                size=20,
                weight=ft.FontWeight.BOLD
            ))
            
            basic_info = ft.Column([
                ft.Text(f"Username: @{data.get('username', 'N/A')}"),
                ft.Text(f"User ID: {data.get('userID', 'N/A')}"),
                ft.Text(f"Nome Completo: {data.get('full_name', 'N/A')}"),
                ft.Text(f"Verificado: {'Sim' if data.get('is_verified') else 'Não'}"),
                ft.Text(f"Conta Business: {'Sim' if data.get('is_business') else 'Não'}"),
                ft.Text(f"Conta Privada: {'Sim' if data.get('is_private') else 'Não'}"),
            ])
            results_container.controls.append(basic_info)
            
            # Adiciona estatísticas
            results_container.controls.append(ft.Text(
                "ESTATÍSTICAS",
                size=20,
                weight=ft.FontWeight.BOLD,
                margin=ft.margin.only(top=20)
            ))
            
            stats_info = ft.Column([
                ft.Text(f"Seguidores: {data.get('follower_count', 'N/A'):,}".replace(',', '.')),
                ft.Text(f"Seguindo: {data.get('following_count', 'N/A'):,}".replace(',', '.')),
                ft.Text(f"Posts: {data.get('media_count', 'N/A'):,}".replace(',', '.')),
                ft.Text(f"Vídeos IGTV: {data.get('total_igtv_videos', 'N/A')}"),
            ])
            results_container.controls.append(stats_info)
            
            # Adiciona informações de contato
            results_container.controls.append(ft.Text(
                "INFORMAÇÕES DE CONTATO",
                size=20,
                weight=ft.FontWeight.BOLD,
                margin=ft.margin.only(top=20)
            ))
            
            contact_info = ft.Column([])
            
            if data.get('public_email'):
                contact_info.controls.append(ft.Text(f"Email Público: {data['public_email']}"))
            
            if data.get('public_phone_number'):
                phone = f"+{data.get('public_phone_country_code', '')} {data['public_phone_number']}"
                contact_info.controls.append(ft.Text(f"Telefone Público: {phone}"))
            
            if data.get('obfuscated_email'):
                contact_info.controls.append(ft.Text(f"Email Ofuscado: {data['obfuscated_email']}"))
            
            if data.get('obfuscated_phone'):
                contact_info.controls.append(ft.Text(f"Telefone Ofuscado: {data['obfuscated_phone']}"))
            
            contact_info.controls.append(ft.Text(
                f"WhatsApp Vinculado: {'Sim' if data.get('is_whatsapp_linked') else 'Não'}"
            ))
            
            results_container.controls.append(contact_info)
            
            # Adiciona outras informações
            results_container.controls.append(ft.Text(
                "OUTRAS INFORMAÇÕES",
                size=20,
                weight=ft.FontWeight.BOLD,
                margin=ft.margin.only(top=20)
            ))
            
            other_info = ft.Column([])
            
            if data.get('external_url'):
                other_info.controls.append(ft.Text(f"URL Externa: {data['external_url']}"))
            
            if data.get('biography'):
                bio = data['biography'][:100] + "..." if len(data.get('biography', '')) > 100 else data.get('biography', '')
                other_info.controls.append(ft.Text(f"Biografia: {bio}"))
            
            if data.get('hd_profile_pic_url_info', {}).get('url'):
                pic_url = data['hd_profile_pic_url_info']['url']
                other_info.controls.append(ft.Text("Foto de Perfil:"))
                other_info.controls.append(
                    ft.Image(
                        src=pic_url,
                        width=200,
                        height=200,
                        fit=ft.ImageFit.CONTAIN,
                        border_radius=ft.border_radius.all(10),
                    )
                )
            
            results_container.controls.append(other_info)
            
            # Adiciona botões de ação
            results_container.controls.append(ft.Row([
                ft.ElevatedButton(
                    "Visualizar Gráficos",
                    icon=ft.Icons.BAR_CHART,
                    on_click=lambda e: change_view(e, "charts")
                ),
                ft.ElevatedButton(
                    "Exportar Dados",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=lambda e: change_view(e, "export")
                )
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20))
            
            # Adiciona timestamp
            results_container.controls.append(ft.Text(
                f"Investigação concluída em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                italic=True,
                size=12,
                margin=ft.margin.only(top=20)
            ))
            
            page.update()
        
        # Função para exportar dados
        def export_data(e):
            if not page.session_data:
                show_snackbar("Nenhum dado para exportar!", "error")
                return
                
            format_type = export_format_dropdown.value
            if not format_type:
                show_snackbar("Selecione um formato de exportação!", "error")
                return
                
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                username = page.session_data.get('username', 'unknown')
                filename = f"instagram_{username}_{timestamp}"
                
                if format_type == "json":
                    filename += ".json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(page.session_data, f, indent=2, ensure_ascii=False)
                        
                elif format_type == "csv":
                    filename += ".csv"
                    with open(filename, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(['Campo', 'Valor'])
                        
                        for key, value in page.session_data.items():
                            if isinstance(value, dict):
                                continue
                            writer.writerow([key, str(value)])
                
                show_snackbar(f"Dados exportados para: {filename}")
                
            except Exception as e:
                show_snackbar(f"Erro ao exportar: {str(e)}", "error")
        
        # Componentes da interface
        
        # Cabeçalho
        header = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Instagram Investigator",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.PINK_ACCENT_400
                ),
                ft.Text(
                    "Ferramenta para extração de dados de perfis públicos do Instagram",
                    size=16,
                    italic=True
                )
            ]),
            margin=ft.margin.only(bottom=20)
        )
        
        # Barra de navegação
        navbar = ft.Row([
            ft.ElevatedButton(
                "Nova Investigação",
                icon=ft.Icons.SEARCH,
                on_click=lambda e: change_view(e, "search")
            ),
            ft.ElevatedButton(
                "Tutorial",
                icon=ft.Icons.HELP_OUTLINE,
                on_click=lambda e: change_view(e, "tutorial")
            ),
            ft.ElevatedButton(
                "Múltiplas Plataformas",
                icon=ft.Icons.COMPARE,
                on_click=lambda e: change_view(e, "multi_platform")
            ),
            ft.ElevatedButton(
                "Exportar Dados",
                icon=ft.Icons.DOWNLOAD,
                on_click=lambda e: change_view(e, "export")
            ),
            ft.ElevatedButton(
                "Visualizar Gráficos",
                icon=ft.Icons.BAR_CHART,
                on_click=lambda e: change_view(e, "charts")
            ),
            ft.ElevatedButton(
                "Gerenciar Cache",
                icon=ft.Icons.STORAGE,
                on_click=lambda e: change_view(e, "cache")
            ),
        ], alignment=ft.MainAxisAlignment.CENTER)
        
        # Campos de entrada para busca
        username_field = ft.TextField(
            label="Username do Instagram",
            hint_text="Digite o username (sem @)",
            prefix_icon=ft.Icons.PERSON,
            expand=True
        )
        
        session_id_field = ft.TextField(
            label="Session ID do Instagram",
            hint_text="Cole seu Session ID aqui",
            prefix_icon=ft.Icons.KEY,
            password=True,
            can_reveal_password=True,
            expand=True
        )
        
        # Barra de progresso
        progress_text = ft.Text("Processando...", style=ft.TextThemeStyle.BODY_MEDIUM)
        progress_bar = ft.ProgressBar(width=400, visible=False)
        
        # Container para resultados
        results_container = ft.Column(scroll=ft.ScrollMode.AUTO)
        
        # Dropdown para formato de exportação
        export_format_dropdown = ft.Dropdown(
            label="Formato de exportação",
            hint_text="Selecione o formato",
            options=[
                ft.dropdown.Option("json", "JSON"),
                ft.dropdown.Option("csv", "CSV"),
            ],
            width=200
        )
        
        # Definição das visualizações
        search_view = ft.Column([
            ft.Text(
                "Nova Investigação",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            ft.Row([username_field], tight=True),
            ft.Container(height=10),
            ft.Row([session_id_field], tight=True),
            ft.Container(height=20),
            ft.Row(
                [ft.ElevatedButton(
                    "Investigar",
                    icon=ft.Icons.SEARCH,
                    on_click=investigate_profile,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                bgcolor=ft.Colors.PINK_ACCENT_400
                    )
                )],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Container(height=20),
            ft.Row([progress_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([progress_bar], alignment=ft.MainAxisAlignment.CENTER),
        ])
        
        tutorial_view = ft.Column([
            ft.Text(
                "Tutorial: Como obter o Session ID",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            ft.Text(
                "1. Abra o Instagram no navegador e faça login",
                size=16
            ),
            ft.Text(
                "2. Pressione F12 para abrir as ferramentas de desenvolvedor",
                size=16
            ),
            ft.Text(
                "3. Vá na aba 'Application' ou 'Aplicação'",
                size=16
            ),
            ft.Text(
                "4. No menu lateral, clique em 'Cookies' → 'https://www.instagram.com'",
                size=16
            ),
            ft.Text(
                "5. Procure por 'sessionid' e copie o valor",
                size=16
            ),
            ft.Container(height=10),
            ft.Text(
                "⚠️ IMPORTANTE: Mantenha seu session ID seguro e não compartilhe!",
                size=16,
                color=ft.Colors.AMBER,
                weight=ft.FontWeight.BOLD
            ),
            ft.Container(height=20),
            ft.Text(
                "⚠️ AVISO LEGAL: Esta ferramenta deve ser usada apenas para fins educacionais e de pesquisa. O uso indevido pode violar os Termos de Serviço do Instagram.",
                size=14,
                color=ft.Colors.RED_400,
                italic=True
            ),
        ])
        
        results_view = ft.Column([
            ft.Text(
                "Resultados da Investigação",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            results_container
        ])
        
        export_view = ft.Column([
            ft.Text(
                "Exportar Dados",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            ft.Row([export_format_dropdown], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Row(
                [ft.ElevatedButton(
                    "Exportar",
                    icon=ft.Icons.DOWNLOAD,
                    on_click=export_data,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE
                    )
                )],
                alignment=ft.MainAxisAlignment.CENTER
            ),
        ])
        
        # Visualização de cache
        cache_stats_container = ft.Column([])
        
        cache_view = ft.Column([
            ft.Text(
                "Gerenciamento de Cache",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            ft.Text(
                "O sistema de cache reduz o número de requisições à API do Instagram, melhorando o desempenho e evitando rate limiting.",
                size=16
            ),
            ft.Container(height=20),
            
            # Estatísticas de cache
            ft.Container(
                content=cache_stats_container,
                padding=10,
                border=ft.border.all(1, ft.Colors.GREY_400),
                border_radius=5,
                margin=ft.margin.only(bottom=20)
            ),
            
            # Botões de ação
            ft.Row([
                ft.ElevatedButton(
                    "Limpar Cache",
                    icon=ft.Icons.DELETE,
                    on_click=clear_cache,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_400
                    )
                ),
                ft.ElevatedButton(
                    "Atualizar Estatísticas",
                    icon=ft.Icons.REFRESH,
                    on_click=lambda e: update_cache_stats()
                ),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
        ])
        
        # Visualização de gráficos
        charts_container = ft.Column([])
        
        charts_view = ft.Column([
            ft.Text(
                "Visualização de Dados",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            ft.Text(
                "Gráficos e visualizações para análise dos dados coletados",
                size=16
            ),
            ft.Container(height=20),
            charts_container,
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    "Voltar aos Resultados",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: change_view(e, "results")
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])
        
        # Função para gerar os gráficos
        def generate_charts(user_data):
            # Limpa o container de gráficos
            charts_container.controls.clear()
            
            if not user_data:
                charts_container.controls.append(
                    ft.Text("Não há dados disponíveis para gerar gráficos.", size=16, color=ft.Colors.RED_400)
                )
                return
            
            # Gera os gráficos
            engagement_chart = data_viz.generate_engagement_chart(user_data)
            activity_chart = data_viz.generate_activity_chart(user_data)
            profile_chart = data_viz.generate_profile_summary(user_data)
            
            # Adiciona os gráficos ao container
            if engagement_chart:
                charts_container.controls.append(
                    ft.Column([
                        ft.Text("Métricas de Engajamento", size=18, weight=ft.FontWeight.BOLD),
                        ft.Image(
                            src=f"data:image/png;base64,{engagement_chart}",
                            width=600,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        ft.Container(height=20)
                    ])
                )
            
            if activity_chart:
                charts_container.controls.append(
                    ft.Column([
                        ft.Text("Métricas de Atividade", size=18, weight=ft.FontWeight.BOLD),
                        ft.Image(
                            src=f"data:image/png;base64,{activity_chart}",
                            width=600,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        ft.Container(height=20)
                    ])
                )
            
            if profile_chart:
                charts_container.controls.append(
                    ft.Column([
                        ft.Text("Características do Perfil", size=18, weight=ft.FontWeight.BOLD),
                        ft.Image(
                            src=f"data:image/png;base64,{profile_chart}",
                            width=600,
                            fit=ft.ImageFit.CONTAIN
                        ),
                        ft.Container(height=20)
                    ])
                )
            
            # Se nenhum gráfico foi gerado
            if not charts_container.controls:
                charts_container.controls.append(
                    ft.Text("Não foi possível gerar gráficos para este perfil.", size=16, color=ft.Colors.RED_400)
                )
            
            page.update()
        
        # Visualização de processamento em lote
        batch_profiles_input = ft.TextField(
            label="Perfis para investigação em lote",
            multiline=True,
            min_lines=5,
            max_lines=10,
            hint_text="Digite um nome de usuário por linha ou separados por vírgula",
            width=600
        )
        
        batch_session_id_field = ft.TextField(
            label="Session ID",
            width=600,
            password=True,
            can_reveal_password=True
        )
        
        batch_progress_text = ft.Text(
            "Aguardando início do processamento...",
            size=14,
            color=ft.Colors.GREY_400,
            visible=False
        )
        
        batch_progress_bar = ft.ProgressBar(
            width=600,
            color=ft.Colors.PINK_ACCENT_400,
                bgcolor=ft.Colors.PINK_100,
            visible=False
        )
        
        batch_results_text = ft.Text(
            "",
            size=14,
            visible=False
        )
        
        batch_results_container = ft.Container(
            content=ft.Column([
                ft.Text(
                    "Resultados do Processamento em Lote",
                    size=18,
                    weight=ft.FontWeight.BOLD
                ),
                batch_results_text,
                ft.Container(height=10),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Perfil")),
                        ft.DataColumn(ft.Text("Status")),
                        ft.DataColumn(ft.Text("Detalhes"))
                    ],
                    rows=[],
                ),
            ]),
            visible=False,
            padding=20,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=10,
            width=600
        )
        
        # Visualização de múltiplas plataformas
        multi_platform_results_container = ft.Column(scroll=ft.ScrollMode.AUTO)
        
        # Inicializa a visualização multiplataforma
        def initialize_multi_platform_view():
            # Cria uma instância da classe MultiPlatformView
            multi_platform_view_instance = MultiPlatformView(page)
            # Retorna o container principal da visualização
            return multi_platform_view_instance.build()
        
        # Define a visualização multiplataforma
        multi_platform_view = initialize_multi_platform_view()
        
        batch_view = ft.Column([
            ft.Text(
                "Investigação em Lote",
                size=24,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=20),
            ft.Text(
                "Adicione múltiplos perfis para investigação em lote.",
                size=16,
                text_align=ft.TextAlign.CENTER
            ),
            ft.Container(height=10),
            ft.Row([batch_profiles_input], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=10),
            ft.Row([batch_session_id_field], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    "Iniciar Processamento",
                    icon=ft.Icons.PLAY_ARROW,
                    on_click=start_batch_processing,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.PINK_ACCENT_400
                    )
                ),
                ft.ElevatedButton(
                    "Parar Processamento",
                    icon=ft.Icons.STOP,
                    on_click=stop_batch_processing,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor=ft.Colors.RED_400
                    ),
                    visible=False
                )
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            ft.Row([batch_progress_text], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([batch_progress_bar], alignment=ft.MainAxisAlignment.CENTER),
            ft.Container(height=20),
            batch_results_container,
            ft.Container(height=20),
            ft.Row([
                ft.ElevatedButton(
                    "Voltar ao Menu Principal",
                    icon=ft.Icons.ARROW_BACK,
                    on_click=lambda e: change_view(e, "main")
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], scroll=ft.ScrollMode.AUTO)
        
        # Função para salvar configurações das plataformas
        def save_platform_settings(settings):
            try:
                # Cria o diretório .env se não existir
                env_dir = os.path.dirname(os.path.abspath(".env"))
                os.makedirs(env_dir, exist_ok=True)
                
                # Lê o arquivo .env existente ou cria um novo
                env_path = os.path.join(env_dir, ".env")
                env_content = ""
                if os.path.exists(env_path):
                    with open(env_path, "r") as f:
                        env_content = f.read()
                
                # Atualiza as configurações para cada plataforma
                for platform, config in settings.items():
                    for key, value in config.items():
                        if value:  # Só adiciona se tiver valor
                            env_var = f"{platform.upper()}_{key.upper()}"
                            
                            # Verifica se a variável já existe no arquivo
                            if f"{env_var}=" in env_content:
                                # Substitui o valor existente
                                lines = env_content.split("\n")
                                for i, line in enumerate(lines):
                                    if line.startswith(f"{env_var}="):
                                        lines[i] = f"{env_var}={value}"
                                env_content = "\n".join(lines)
                            else:
                                # Adiciona nova variável
                                env_content += f"\n{env_var}={value}"
                
                # Salva o arquivo .env atualizado
                with open(env_path, "w") as f:
                    f.write(env_content)
                    
                # Recarrega as variáveis de ambiente
                load_dotenv(override=True)
                
                show_snackbar("Configurações salvas com sucesso!")
                
            except Exception as e:
                show_snackbar(f"Erro ao salvar configurações: {str(e)}", "error")
        
        # Dicionário de visualizações
        views = {
            "main": main_view,
            "search": search_view,
            "tutorial": tutorial_view,
            "results": results_view,
            "export": export_view,
            "cache": cache_view,
            "charts": charts_view,
            "batch": batch_view,
            "multi_platform": multi_platform_view,
            "multi_platform_results": multi_platform_results_container
        }
        
        # Container principal para conteúdo
        content_container = ft.Container(
            content=main_view,
            expand=True,
            margin=ft.margin.only(top=20)
        )
        
        # Rodapé
        footer = ft.Container(
            content=ft.Row(
                [
                    ft.Text(
                        "© 2024 Instagram Investigator | Desenvolvido para fins educacionais",
                        size=12,
                        color=ft.Colors.GREY_400
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            margin=ft.margin.only(top=20)
        )
        
        # Adiciona elementos à página
        page.add(
            header,
            navbar,
            content_container,
            footer
        )


if __name__ == "__main__":
    ft.app(target=InstagramInvestigator.main)