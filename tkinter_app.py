#!/usr/bin/env python3
"""
Aplicação Principal do Instagram Investigator com Tkinter
Interface gráfica moderna usando Tkinter para análise cross-platform
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Adicionar o diretório modules ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Importar módulos do projeto
from modules.instagram_api import InstagramAPI
from modules.facebook_api import FacebookAPI
from modules.cross_platform_analyzer import CrossPlatformAnalyzer
from modules.tkinter_visualizations import TkinterVisualizationManager
from modules.export_manager import ExportManager
from modules.cache_manager import CacheManager
from modules.logging_manager import setup_logging, get_logging_manager
from modules.system_monitor import setup_monitoring, get_system_monitor

try:
    from modules.twitter_api import TwitterAPI
    TWITTER_AVAILABLE = True
except ImportError:
    TWITTER_AVAILABLE = False

try:
    from modules.linkedin_api import LinkedInAPI
    LINKEDIN_AVAILABLE = True
except ImportError:
    LINKEDIN_AVAILABLE = False

try:
    from modules.tiktok_api import TikTokAPI
    TIKTOK_AVAILABLE = True
except ImportError:
    TIKTOK_AVAILABLE = False

class InstagramInvestigatorApp:
    """
    Aplicação principal do Instagram Investigator com interface Tkinter
    """
    
    def __init__(self):
        """
        Inicializa a aplicação
        """
        self.root = tk.Tk()
        self.root.title("Instagram Investigator - Análise Cross-Platform")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 600)
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Cores do tema
        self.colors = {
            'primary': '#1565C0',
            'secondary': '#1976D2',
            'success': '#4CAF50',
            'warning': '#FF9800',
            'error': '#F44336',
            'background': '#F5F5F5',
            'surface': '#FFFFFF',
            'text': '#212121',
            'text_secondary': '#666666'
        }
        
        # Configurar estilos personalizados
        self._configure_styles()
        
        # Configurar sistema de logging e monitoramento
        self._setup_logging_and_monitoring()
        
        # Logger da aplicação
        self.logger = logging.getLogger(f"{__name__}.InstagramInvestigatorApp")
        self.logger.info("Iniciando Instagram Investigator v2.0")
        
        # Inicializar componentes
        self.apis = {}
        self.cross_analyzer = CrossPlatformAnalyzer()
        self.cross_visualizer = TkinterVisualizationManager()
        self.export_manager = ExportManager()
        self.cache_manager = CacheManager()
        
        # Gerenciadores de logging e monitoramento
        self.logging_manager = get_logging_manager()
        self.system_monitor = get_system_monitor()
        
        # Dados da aplicação
        self.platform_data = {}
        self.cross_analysis_results = {}
        self.search_in_progress = False
        
        # Variáveis de controle
        self.username_var = tk.StringVar()
        self.platform_vars = {
            'instagram': tk.BooleanVar(value=True),
            'facebook': tk.BooleanVar(value=False),
            'twitter': tk.BooleanVar(value=False),
            'linkedin': tk.BooleanVar(value=False),
            'tiktok': tk.BooleanVar(value=False)
        }
        
        # Inicializar APIs
        self._initialize_apis()
        
        # Criar interface
        self._create_interface()
        
        # Configurar eventos
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Log de inicialização completa
        self.logger.info("Interface inicializada com sucesso")
        self.logging_manager.log_user_action("app_started", metadata={"version": "2.0"})
    
    def _setup_logging_and_monitoring(self):
        """
        Configura sistema de logging e monitoramento
        """
        # Configurar logging
        setup_logging(
            log_dir="logs",
            log_level="INFO",
            enable_metrics=True
        )
        
        # Configurar monitoramento
        setup_monitoring(check_interval=60)  # Verificar a cada minuto
        
        # Iniciar monitoramento
        monitor = get_system_monitor()
        monitor.start_monitoring()
    
    def _configure_styles(self):
        """
        Configura estilos personalizados para a interface
        """
        # Configurar cores do tema
        self.style.configure('Title.TLabel', 
                           font=('Segoe UI', 24, 'bold'),
                           foreground=self.colors['primary'])
        
        self.style.configure('Subtitle.TLabel',
                           font=('Segoe UI', 12),
                           foreground=self.colors['text_secondary'])
        
        self.style.configure('Header.TLabel',
                           font=('Segoe UI', 14, 'bold'),
                           foreground=self.colors['text'])
        
        self.style.configure('Primary.TButton',
                           font=('Segoe UI', 10, 'bold'))
        
        self.style.configure('Success.TLabel',
                           foreground=self.colors['success'])
        
        self.style.configure('Error.TLabel',
                           foreground=self.colors['error'])
        
        self.style.configure('Warning.TLabel',
                           foreground=self.colors['warning'])
    
    def _initialize_apis(self):
        """
        Inicializa as APIs das plataformas
        """
        try:
            # Instagram API
            self.apis['instagram'] = InstagramAPI()
            
            # Facebook API
            self.apis['facebook'] = FacebookAPI()
            
            # APIs opcionais
            if TWITTER_AVAILABLE:
                self.apis['twitter'] = TwitterAPI()
            
            if LINKEDIN_AVAILABLE:
                self.apis['linkedin'] = LinkedInAPI()
            
            if TIKTOK_AVAILABLE:
                self.apis['tiktok'] = TikTokAPI()
                
        except Exception as e:
            messagebox.showerror("Erro de Inicialização", 
                               f"Erro ao inicializar APIs: {str(e)}")
    
    def _create_interface(self):
        """
        Cria a interface principal da aplicação
        """
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, 
                              text="Instagram Investigator",
                              style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        subtitle_label = ttk.Label(main_frame,
                                 text="Análise e comparação de perfis em múltiplas redes sociais",
                                 style='Subtitle.TLabel')
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Notebook para abas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Criar abas
        self._create_search_tab()
        self._create_results_tab()
        self._create_visualizations_tab()
        self._create_export_tab()
        self._create_settings_tab()
        
        # Barra de status
        self.status_var = tk.StringVar(value="Pronto")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var,
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _create_search_tab(self):
        """
        Cria a aba de pesquisa
        """
        search_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(search_frame, text="🔍 Pesquisa")
        
        # Campo de usuário
        ttk.Label(search_frame, text="Nome de usuário:", 
                 style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        username_entry = ttk.Entry(search_frame, textvariable=self.username_var,
                                 font=('Segoe UI', 12), width=40)
        username_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Seleção de plataformas
        ttk.Label(search_frame, text="Plataformas:", 
                 style='Header.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        platforms_frame = ttk.LabelFrame(search_frame, text="Selecione as plataformas", padding="10")
        platforms_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Checkboxes das plataformas
        platform_info = {
            'instagram': ('📷 Instagram', True),
            'facebook': ('📘 Facebook', TWITTER_AVAILABLE),
            'twitter': ('🐦 Twitter/X', TWITTER_AVAILABLE),
            'linkedin': ('💼 LinkedIn', LINKEDIN_AVAILABLE),
            'tiktok': ('🎵 TikTok', TIKTOK_AVAILABLE)
        }
        
        row = 0
        col = 0
        for platform, (label, available) in platform_info.items():
            if available:
                cb = ttk.Checkbutton(platforms_frame, text=label,
                                   variable=self.platform_vars[platform])
                cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=5)
                col += 1
                if col > 2:
                    col = 0
                    row += 1
        
        # Botão de pesquisa
        self.search_button = ttk.Button(search_frame, text="🔍 Iniciar Pesquisa",
                                      command=self._start_search,
                                      style='Primary.TButton')
        self.search_button.grid(row=4, column=0, pady=20)
        
        # Barra de progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(search_frame, variable=self.progress_var,
                                          mode='indeterminate')
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status da pesquisa
        self.search_status_var = tk.StringVar()
        self.search_status_label = ttk.Label(search_frame, textvariable=self.search_status_var)
        self.search_status_label.grid(row=6, column=0, columnspan=2)
        
        # Configurar grid
        search_frame.columnconfigure(1, weight=1)
        platforms_frame.columnconfigure(2, weight=1)
    
    def _create_results_tab(self):
        """
        Cria a aba de resultados
        """
        results_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(results_frame, text="📊 Resultados")
        
        # Título
        ttk.Label(results_frame, text="Resultados da Pesquisa",
                 style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Frame com scroll para resultados
        canvas = tk.Canvas(results_frame, bg='white')
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        self.results_scrollable_frame = ttk.Frame(canvas)
        
        self.results_scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.results_scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Configurar grid
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Mensagem inicial
        self.no_results_label = ttk.Label(self.results_scrollable_frame,
                                        text="Nenhuma pesquisa realizada ainda.\nUse a aba 'Pesquisa' para começar.",
                                        style='Subtitle.TLabel',
                                        justify=tk.CENTER)
        self.no_results_label.grid(row=0, column=0, pady=50)
    
    def _create_visualizations_tab(self):
        """
        Cria a aba de visualizações
        """
        viz_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(viz_frame, text="📈 Visualizações")
        
        ttk.Label(viz_frame, text="Visualizações Avançadas",
                 style='Title.TLabel').grid(row=0, column=0, pady=(0, 20))
        
        # Frame para visualizações
        self.viz_content_frame = ttk.Frame(viz_frame)
        self.viz_content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Mensagem inicial
        self.viz_initial_label = ttk.Label(self.viz_content_frame,
                 text="As visualizações aparecerão aqui após uma pesquisa bem-sucedida.",
                 style='Subtitle.TLabel')
        self.viz_initial_label.grid(row=0, column=0, pady=50)
        
        viz_frame.columnconfigure(0, weight=1)
        viz_frame.rowconfigure(1, weight=1)
    
    def _create_export_tab(self):
        """
        Cria a aba de exportação
        """
        export_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(export_frame, text="💾 Exportação")
        
        ttk.Label(export_frame, text="Exportação de Dados",
                 style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status dos dados
        self.export_status_frame = ttk.LabelFrame(export_frame, text="Status dos Dados", padding="10")
        self.export_status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.data_status_var = tk.StringVar(value="Nenhum dado disponível para exportação")
        self.data_status_label = ttk.Label(self.export_status_frame, textvariable=self.data_status_var,
                                         style='Warning.TLabel')
        self.data_status_label.grid(row=0, column=0)
        
        # Formatos de exportação
        formats_frame = ttk.LabelFrame(export_frame, text="Formatos de Exportação", padding="10")
        formats_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.export_format_vars = {
            'json': tk.BooleanVar(value=True),
            'csv': tk.BooleanVar(value=True),
            'pdf': tk.BooleanVar(value=True),
            'excel': tk.BooleanVar(value=False)
        }
        
        format_labels = {
            'json': '📄 JSON - Dados estruturados',
            'csv': '📊 CSV - Planilha simples',
            'pdf': '📋 PDF - Relatório visual',
            'excel': '📈 Excel - Planilha avançada'
        }
        
        for i, (fmt, label) in enumerate(format_labels.items()):
            ttk.Checkbutton(formats_frame, text=label,
                          variable=self.export_format_vars[fmt]).grid(row=i//2, column=i%2, 
                                                                     sticky=tk.W, padx=10, pady=5)
        
        # Botão de exportação
        self.export_button = ttk.Button(export_frame, text="💾 Exportar Dados",
                                      command=self._export_data,
                                      state='disabled')
        self.export_button.grid(row=3, column=0, pady=20)
        
        # Histórico de exportações
        history_frame = ttk.LabelFrame(export_frame, text="Histórico de Exportações", padding="10")
        history_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Treeview para histórico
        self.history_tree = ttk.Treeview(history_frame, columns=('format', 'size', 'date'), show='headings')
        self.history_tree.heading('format', text='Formato')
        self.history_tree.heading('size', text='Tamanho')
        self.history_tree.heading('date', text='Data')
        self.history_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar para histórico
        history_scroll = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        history_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.history_tree.configure(yscrollcommand=history_scroll.set)
        
        # Configurar grid
        export_frame.columnconfigure(1, weight=1)
        export_frame.rowconfigure(4, weight=1)
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Atualizar histórico
        self._update_export_history()
    
    def _create_settings_tab(self):
        """
        Cria a aba de configurações
        """
        settings_frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(settings_frame, text="⚙️ Configurações")
        
        ttk.Label(settings_frame, text="Configurações das APIs",
                 style='Title.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Notebook para configurações das plataformas
        settings_notebook = ttk.Notebook(settings_frame)
        settings_notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurações do Instagram
        self._create_instagram_settings(settings_notebook)
        
        # Configurações do Facebook
        self._create_facebook_settings(settings_notebook)
        
        # Botão salvar
        ttk.Button(settings_frame, text="💾 Salvar Configurações",
                 command=self._save_settings).grid(row=2, column=0, pady=20)
        
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.rowconfigure(1, weight=1)
    
    def _create_instagram_settings(self, parent):
        """
        Cria configurações do Instagram
        """
        instagram_frame = ttk.Frame(parent, padding="20")
        parent.add(instagram_frame, text="📷 Instagram")
        
        ttk.Label(instagram_frame, text="Configurações do Instagram",
                 style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Campos de configuração
        ttk.Label(instagram_frame, text="Nome de usuário:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.instagram_username_var = tk.StringVar()
        ttk.Entry(instagram_frame, textvariable=self.instagram_username_var,
                 width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(instagram_frame, text="Senha:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.instagram_password_var = tk.StringVar()
        ttk.Entry(instagram_frame, textvariable=self.instagram_password_var,
                 show="*", width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        instagram_frame.columnconfigure(1, weight=1)
    
    def _create_facebook_settings(self, parent):
        """
        Cria configurações do Facebook
        """
        facebook_frame = ttk.Frame(parent, padding="20")
        parent.add(facebook_frame, text="📘 Facebook")
        
        ttk.Label(facebook_frame, text="Configurações do Facebook",
                 style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Campos de configuração
        ttk.Label(facebook_frame, text="App ID:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.facebook_app_id_var = tk.StringVar()
        ttk.Entry(facebook_frame, textvariable=self.facebook_app_id_var,
                 width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(facebook_frame, text="App Secret:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.facebook_app_secret_var = tk.StringVar()
        ttk.Entry(facebook_frame, textvariable=self.facebook_app_secret_var,
                 show="*", width=40).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        ttk.Label(facebook_frame, text="Access Token:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.facebook_token_var = tk.StringVar()
        ttk.Entry(facebook_frame, textvariable=self.facebook_token_var,
                 show="*", width=40).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        facebook_frame.columnconfigure(1, weight=1)
    
    def _start_search(self):
        """
        Inicia a pesquisa em múltiplas plataformas
        """
        username = self.username_var.get().strip()
        if not username:
            self.logger.warning("Tentativa de pesquisa sem nome de usuário")
            messagebox.showerror("Erro", "Digite um nome de usuário")
            return
        
        # Verificar plataformas selecionadas
        selected_platforms = [platform for platform, var in self.platform_vars.items() 
                            if var.get() and platform in self.apis]
        
        if not selected_platforms:
            self.logger.warning(f"Tentativa de pesquisa sem plataformas selecionadas para usuário: {username}")
            messagebox.showerror("Erro", "Selecione pelo menos uma plataforma")
            return
        
        # Log da ação do usuário
        self.logger.info(f"Iniciando pesquisa para usuário: {username} em plataformas: {selected_platforms}")
        self.logging_manager.log_user_action(
            "search_started",
            metadata={
                "username": username,
                "platforms": selected_platforms,
                "platform_count": len(selected_platforms)
            }
        )
        
        # Iniciar pesquisa em thread separada
        self.search_in_progress = True
        self.search_button.config(state='disabled')
        self.progress_bar.start()
        self.search_status_var.set("Iniciando pesquisa...")
        
        thread = threading.Thread(target=self._perform_search, 
                                args=(username, selected_platforms))
        thread.daemon = True
        thread.start()
    
    def _perform_search(self, username: str, platforms: List[str]):
        """
        Executa a pesquisa nas plataformas selecionadas
        
        Args:
            username: Nome de usuário para pesquisar
            platforms: Lista de plataformas selecionadas
        """
        import time
        
        search_start_time = time.time()
        
        try:
            self.platform_data = {}
            successful_platforms = []
            failed_platforms = []
            
            for i, platform in enumerate(platforms):
                # Atualizar status
                self.root.after(0, lambda p=platform: 
                              self.search_status_var.set(f"Pesquisando em {p.capitalize()}..."))
                
                platform_start_time = time.time()
                
                try:
                    if platform in self.apis:
                        self.logger.debug(f"Iniciando busca na API {platform} para usuário {username}")
                        
                        data = self.apis[platform].get_user_profile(username)
                        platform_duration = time.time() - platform_start_time
                        
                        if data:
                            self.platform_data[platform] = data
                            successful_platforms.append(platform)
                            
                            # Log da chamada de API bem-sucedida
                            self.logging_manager.log_api_call(
                                platform=platform,
                                endpoint="get_user_profile",
                                success=True,
                                duration=platform_duration,
                                response_size=len(str(data)) if data else 0
                            )
                            
                            self.logger.info(f"Dados obtidos com sucesso de {platform} em {platform_duration:.2f}s")
                        else:
                            failed_platforms.append(platform)
                            self.logger.warning(f"Nenhum dado retornado de {platform} para usuário {username}")
                            
                            # Log da chamada de API sem dados
                            self.logging_manager.log_api_call(
                                platform=platform,
                                endpoint="get_user_profile",
                                success=False,
                                duration=platform_duration,
                                error_message="No data returned"
                            )
                            
                except Exception as e:
                    platform_duration = time.time() - platform_start_time
                    failed_platforms.append(platform)
                    
                    error_msg = str(e)
                    self.logger.error(f"Erro ao pesquisar em {platform}: {error_msg}")
                    
                    # Log da chamada de API com erro
                    self.logging_manager.log_api_call(
                        platform=platform,
                        endpoint="get_user_profile",
                        success=False,
                        duration=platform_duration,
                        error_message=error_msg
                    )
                    continue
            
            # Realizar análise cruzada se houver dados de múltiplas plataformas
            cross_analysis_duration = 0
            if len(self.platform_data) > 1:
                self.root.after(0, lambda: self.search_status_var.set("Realizando análise cruzada..."))
                
                cross_start_time = time.time()
                self.cross_analysis_results = self.cross_analyzer.analyze_cross_platform(
                    self.platform_data
                )
                cross_analysis_duration = time.time() - cross_start_time
                
                self.logger.info(f"Análise cruzada concluída em {cross_analysis_duration:.2f}s")
                
                # Log da performance da análise cruzada
                self.logging_manager.log_performance(
                    operation="cross_platform_analysis",
                    duration=cross_analysis_duration,
                    success=True,
                    metadata={
                        "platforms_analyzed": len(self.platform_data),
                        "username": username
                    }
                )
            
            # Log do resultado geral da pesquisa
            total_duration = time.time() - search_start_time
            self.logging_manager.log_performance(
                operation="complete_search",
                duration=total_duration,
                success=len(successful_platforms) > 0,
                metadata={
                    "username": username,
                    "total_platforms": len(platforms),
                    "successful_platforms": successful_platforms,
                    "failed_platforms": failed_platforms,
                    "cross_analysis_performed": len(self.platform_data) > 1
                }
            )
            
            self.logger.info(f"Pesquisa concluída em {total_duration:.2f}s - Sucessos: {len(successful_platforms)}, Falhas: {len(failed_platforms)}")
            
            # Atualizar interface
            self.root.after(0, self._search_completed)
            
        except Exception as e:
            self.root.after(0, lambda: self._search_error(str(e)))
    
    def _search_completed(self):
        """
        Callback executado quando a pesquisa é concluída
        """
        self.search_in_progress = False
        self.search_button.config(state='normal')
        self.progress_bar.stop()
        
        if self.platform_data:
            platforms_found = ", ".join(self.platform_data.keys())
            self.search_status_var.set(f"Pesquisa concluída! Dados encontrados: {platforms_found}")
            
            # Log de sucesso
            self.logger.info(f"Pesquisa concluída com sucesso - Plataformas: {platforms_found}")
            self.logging_manager.log_user_action(
                "search_completed",
                metadata={
                    "platforms_found": list(self.platform_data.keys()),
                    "platform_count": len(self.platform_data),
                    "has_cross_analysis": len(self.platform_data) > 1
                }
            )
            
            # Atualizar aba de resultados
            self._update_results_display()
            self._update_visualizations()
            
            # Habilitar exportação
            self.export_button.config(state='normal')
            self.data_status_var.set(f"Dados disponíveis: {len(self.platform_data)} plataforma(s)")
            self.data_status_label.config(style='Success.TLabel')
            
            # Mudar para aba de resultados
            self.notebook.select(1)
            
        else:
            self.search_status_var.set("Nenhum dado encontrado")
            
            # Log de pesquisa sem resultados
            self.logger.warning("Pesquisa concluída sem dados encontrados")
            self.logging_manager.log_user_action(
                "search_no_results",
                metadata={"message": "No data found for specified user"}
            )
            
            messagebox.showwarning("Aviso", "Nenhum dado foi encontrado para o usuário especificado")
    
    def _search_error(self, error_message: str):
        """
        Callback executado quando há erro na pesquisa
        
        Args:
            error_message: Mensagem de erro
        """
        self.search_in_progress = False
        self.search_button.config(state='normal')
        self.progress_bar.stop()
        self.search_status_var.set(f"Erro na pesquisa: {error_message}")
        
        # Log de erro detalhado
        self.logger.error(f"Erro durante a pesquisa: {error_message}")
        self.logging_manager.log_user_action(
            "search_error",
            metadata={
                "error_message": error_message,
                "error_type": "search_failure"
            }
        )
        
        messagebox.showerror("Erro na Pesquisa", f"Erro durante a pesquisa: {error_message}")
    
    def _update_results_display(self):
        """
        Atualiza a exibição dos resultados
        """
        # Limpar resultados anteriores
        for widget in self.results_scrollable_frame.winfo_children():
            widget.destroy()
        
        if not self.platform_data:
            self.no_results_label = ttk.Label(self.results_scrollable_frame,
                                            text="Nenhuma pesquisa realizada ainda.\nUse a aba 'Pesquisa' para começar.",
                                            style='Subtitle.TLabel',
                                            justify=tk.CENTER)
            self.no_results_label.grid(row=0, column=0, pady=50)
            return
        
        # Título dos resultados
        ttk.Label(self.results_scrollable_frame, text="Dados das Plataformas",
                 style='Header.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Criar cards para cada plataforma
        row = 1
        for platform, data in self.platform_data.items():
            self._create_platform_card(self.results_scrollable_frame, platform, data, row)
            row += 1
        
        # Seção de análise cruzada
        if self.cross_analysis_results:
            ttk.Separator(self.results_scrollable_frame, orient='horizontal').grid(
                row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
            row += 1
            
            ttk.Label(self.results_scrollable_frame, text="Análise Cross-Platform",
                     style='Header.TLabel').grid(row=row, column=0, columnspan=2, pady=(0, 10))
            row += 1
            
            self._create_cross_analysis_display(self.results_scrollable_frame, row)
    
    def _create_platform_card(self, parent, platform: str, data: Dict[str, Any], row: int):
        """
        Cria um card para exibir dados de uma plataforma
        
        Args:
            parent: Widget pai
            platform: Nome da plataforma
            data: Dados da plataforma
            row: Linha para posicionar o card
        """
        # Frame do card
        card_frame = ttk.LabelFrame(parent, text=f"📱 {platform.capitalize()}", padding="15")
        card_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        # Informações básicas
        info_frame = ttk.Frame(card_frame)
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Nome e usuário
        if data.get('full_name'):
            ttk.Label(info_frame, text=f"Nome: {data['full_name']}",
                     font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
        
        if data.get('username'):
            ttk.Label(info_frame, text=f"Usuário: @{data['username']}").grid(row=1, column=0, sticky=tk.W)
        
        # Estatísticas
        stats_text = []
        if data.get('followers_count') is not None:
            stats_text.append(f"Seguidores: {data['followers_count']:,}")
        if data.get('following_count') is not None:
            stats_text.append(f"Seguindo: {data['following_count']:,}")
        if data.get('posts_count') is not None:
            stats_text.append(f"Posts: {data['posts_count']:,}")
        
        if stats_text:
            ttk.Label(info_frame, text=" | ".join(stats_text)).grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # Biografia
        if data.get('biography'):
            bio_text = data['biography'][:100] + "..." if len(data['biography']) > 100 else data['biography']
            ttk.Label(info_frame, text=f"Bio: {bio_text}",
                     wraplength=400).grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        # Verificado
        if data.get('is_verified'):
            ttk.Label(info_frame, text="✅ Verificado",
                     foreground='blue').grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        
        card_frame.columnconfigure(0, weight=1)
        parent.columnconfigure(0, weight=1)
    
    def _create_cross_analysis_display(self, parent, row: int):
        """
        Cria a exibição da análise cruzada
        
        Args:
            parent: Widget pai
            row: Linha inicial
        """
        analysis_frame = ttk.LabelFrame(parent, text="🔍 Análise Cross-Platform", padding="15")
        analysis_frame.grid(row=row, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        # Correspondência de identidade
        if 'identity_match' in self.cross_analysis_results:
            identity_data = self.cross_analysis_results['identity_match']
            ttk.Label(analysis_frame, text="Correspondência de Identidade:",
                     font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky=tk.W)
            
            match_score = identity_data.get('confidence_score', 0)
            color = 'green' if match_score > 0.7 else 'orange' if match_score > 0.4 else 'red'
            ttk.Label(analysis_frame, text=f"Confiança: {match_score:.1%}",
                     foreground=color).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # Sobreposição de audiência
        if 'audience_overlap' in self.cross_analysis_results:
            overlap_data = self.cross_analysis_results['audience_overlap']
            ttk.Label(analysis_frame, text="Sobreposição de Audiência:",
                     font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
            
            overlap_pct = overlap_data.get('overlap_percentage', 0)
            ttk.Label(analysis_frame, text=f"Sobreposição: {overlap_pct:.1%}").grid(
                row=1, column=1, sticky=tk.W, padx=(20, 0), pady=(10, 0))
        
        # Similaridade de conteúdo
        if 'content_similarity' in self.cross_analysis_results:
            content_data = self.cross_analysis_results['content_similarity']
            ttk.Label(analysis_frame, text="Similaridade de Conteúdo:",
                     font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
            
            similarity_score = content_data.get('similarity_score', 0)
            ttk.Label(analysis_frame, text=f"Similaridade: {similarity_score:.1%}").grid(
                row=2, column=1, sticky=tk.W, padx=(20, 0), pady=(10, 0))
        
        parent.columnconfigure(0, weight=1)
    
    def _export_data(self):
        """
        Exporta os dados coletados
        """
        if not self.platform_data:
            self.logger.warning("Tentativa de exportação sem dados disponíveis")
            messagebox.showwarning("Aviso", "Nenhum dado disponível para exportação")
            return
        
        # Verificar formatos selecionados
        selected_formats = [fmt for fmt, var in self.export_format_vars.items() if var.get()]
        
        if not selected_formats:
            self.logger.warning("Tentativa de exportação sem formatos selecionados")
            messagebox.showwarning("Aviso", "Selecione pelo menos um formato para exportação")
            return
        
        # Log do início da exportação
        self.logger.info(f"Iniciando exportação - Formatos: {selected_formats}")
        self.logging_manager.log_user_action(
            "export_started",
            metadata={
                "formats": selected_formats,
                "platforms": list(self.platform_data.keys()),
                "has_analysis": bool(self.cross_analysis_results)
            }
        )
        
        try:
            # Gerar visualizações se disponíveis
            visualizations = {}
            if self.cross_analysis_results:
                try:
                    visualizations = self.cross_visualizer.generate_comprehensive_report(
                        self.platform_data, self.cross_analysis_results
                    )
                except Exception as e:
                    print(f"Erro ao gerar visualizações: {str(e)}")
            
            # Exportar dados
            exported_files = self.export_manager.export_comprehensive_report(
                platform_data=self.platform_data,
                analysis_data=self.cross_analysis_results,
                visualizations=visualizations,
                formats=selected_formats
            )
            
            if exported_files:
                files_list = ", ".join([f"{fmt.upper()}" for fmt in exported_files.keys()])
                
                # Log de sucesso na exportação
                self.logger.info(f"Exportação concluída com sucesso - Arquivos: {files_list}")
                self.logging_manager.log_user_action(
                    "export_completed",
                    metadata={
                        "exported_formats": list(exported_files.keys()),
                        "file_count": len(exported_files),
                        "success": True
                    }
                )
                
                messagebox.showinfo("Sucesso", 
                                  f"Dados exportados com sucesso!\nFormatos: {files_list}")
                
                # Atualizar histórico
                self._update_export_history()
            else:
                # Log de falha na exportação
                self.logger.error("Exportação falhou - nenhum arquivo gerado")
                self.logging_manager.log_user_action(
                    "export_failed",
                    metadata={"error": "No files generated", "success": False}
                )
                messagebox.showerror("Erro", "Erro na exportação - nenhum arquivo gerado")
                
        except Exception as e:
            # Log de erro na exportação
            self.logger.error(f"Erro durante a exportação: {str(e)}")
            self.logging_manager.log_user_action(
                "export_error",
                metadata={"error": str(e), "success": False}
            )
            messagebox.showerror("Erro na Exportação", f"Erro durante a exportação: {str(e)}")
    
    def _update_export_history(self):
        """
        Atualiza o histórico de exportações
        """
        # Limpar histórico atual
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        try:
            history = self.export_manager.get_export_history()
            
            for export in history[:10]:  # Mostrar últimas 10 exportações
                # Formatar tamanho
                size_mb = export['size_bytes'] / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{export['size_bytes'] / 1024:.1f} KB"
                
                # Formatar data
                created_date = datetime.fromisoformat(export['created_at'])
                date_str = created_date.strftime("%d/%m/%Y %H:%M")
                
                self.history_tree.insert('', 'end', values=(
                    export['format'].upper(),
                    size_str,
                    date_str
                ))
                
        except Exception as e:
            print(f"Erro ao atualizar histórico: {str(e)}")
    
    def _save_settings(self):
        """
        Salva as configurações no arquivo .env
        """
        try:
            # Preparar dados para salvar
            settings = {
                'INSTAGRAM_USERNAME': self.instagram_username_var.get(),
                'INSTAGRAM_PASSWORD': self.instagram_password_var.get(),
                'FACEBOOK_APP_ID': self.facebook_app_id_var.get(),
                'FACEBOOK_APP_SECRET': self.facebook_app_secret_var.get(),
                'FACEBOOK_ACCESS_TOKEN': self.facebook_token_var.get()
            }
            
            # Salvar no arquivo .env
            env_path = '.env'
            with open(env_path, 'w', encoding='utf-8') as f:
                for key, value in settings.items():
                    if value:  # Só salvar se não estiver vazio
                        f.write(f"{key}={value}\n")
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            
            # Reinicializar APIs
            self._initialize_apis()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {str(e)}")
    
    def _on_closing(self):
        """
        Callback executado ao fechar a aplicação
        """
        self.logger.info("Iniciando processo de fechamento da aplicação")
        
        if self.search_in_progress:
            if messagebox.askokcancel("Fechar", "Uma pesquisa está em andamento. Deseja realmente fechar?"):
                self._shutdown_application()
        else:
            self._shutdown_application()
    
    def _shutdown_application(self):
        """
        Finaliza a aplicação de forma segura
        """
        try:
            # Log de finalização
            self.logger.info("Finalizando aplicação")
            self.logging_manager.log_user_action("app_closed")
            
            # Parar monitoramento
            if hasattr(self, 'system_monitor'):
                self.system_monitor.shutdown()
            
            # Finalizar sistema de logging
            if hasattr(self, 'logging_manager'):
                self.logging_manager.shutdown()
            
            # Fechar janela
            self.root.destroy()
            
        except Exception as e:
            print(f"Erro ao finalizar aplicação: {e}")
            self.root.destroy()
    
    def run(self):
        """
        Executa a aplicação
        """
        self.root.mainloop()

def main():
    """
    Função principal
    """
    try:
        app = InstagramInvestigatorApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Erro ao inicializar aplicação: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()