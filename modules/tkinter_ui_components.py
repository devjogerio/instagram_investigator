#!/usr/bin/env python3
"""
Componentes de Interface Tkinter para Instagram Investigator
Substitui os componentes baseados em Flet por implementações Tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, List, Any, Optional, Callable
import threading
from datetime import datetime
import os

class TkinterUIComponents:
    """
    Classe para componentes de interface Tkinter reutilizáveis
    """
    
    def __init__(self):
        """
        Inicializa os componentes UI
        """
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
    
    def create_labeled_entry(self, parent: tk.Widget, label_text: str, 
                           variable: tk.StringVar, row: int, column: int = 0,
                           show: str = None, width: int = 30) -> ttk.Entry:
        """
        Cria um campo de entrada com rótulo
        
        Args:
            parent: Widget pai
            label_text: Texto do rótulo
            variable: Variável Tkinter para o valor
            row: Linha para posicionar
            column: Coluna para posicionar
            show: Caractere para mascarar entrada (ex: '*' para senha)
            width: Largura do campo
            
        Returns:
            Widget Entry criado
        """
        # Rótulo
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=column, sticky=tk.W, pady=(5, 2))
        
        # Campo de entrada
        entry = ttk.Entry(parent, textvariable=variable, show=show, width=width)
        entry.grid(row=row+1, column=column, sticky=(tk.W, tk.E), pady=(0, 10))
        
        return entry
    
    def create_platform_checkboxes(self, parent: tk.Widget, platform_vars: Dict[str, tk.BooleanVar],
                                  available_platforms: Dict[str, bool]) -> ttk.LabelFrame:
        """
        Cria checkboxes para seleção de plataformas
        
        Args:
            parent: Widget pai
            platform_vars: Dicionário de variáveis booleanas das plataformas
            available_platforms: Dicionário indicando quais plataformas estão disponíveis
            
        Returns:
            LabelFrame contendo os checkboxes
        """
        frame = ttk.LabelFrame(parent, text="Selecione as Plataformas", padding="10")
        
        platform_info = {
            'instagram': ('📷 Instagram', True),
            'facebook': ('📘 Facebook', available_platforms.get('facebook', False)),
            'twitter': ('🐦 Twitter/X', available_platforms.get('twitter', False)),
            'linkedin': ('💼 LinkedIn', available_platforms.get('linkedin', False)),
            'tiktok': ('🎵 TikTok', available_platforms.get('tiktok', False))
        }
        
        row = 0
        col = 0
        for platform, (label, available) in platform_info.items():
            if available and platform in platform_vars:
                cb = ttk.Checkbutton(frame, text=label,
                                   variable=platform_vars[platform])
                cb.grid(row=row, column=col, sticky=tk.W, padx=10, pady=5)
                col += 1
                if col > 2:
                    col = 0
                    row += 1
        
        return frame
    
    def create_progress_section(self, parent: tk.Widget) -> Dict[str, tk.Widget]:
        """
        Cria seção de progresso com barra e status
        
        Args:
            parent: Widget pai
            
        Returns:
            Dicionário com widgets de progresso
        """
        # Barra de progresso
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(parent, variable=progress_var, mode='indeterminate')
        
        # Status
        status_var = tk.StringVar()
        status_label = ttk.Label(parent, textvariable=status_var)
        
        return {
            'progress_var': progress_var,
            'progress_bar': progress_bar,
            'status_var': status_var,
            'status_label': status_label
        }
    
    def create_data_card(self, parent: tk.Widget, title: str, data: Dict[str, Any],
                        row: int, column: int = 0) -> ttk.LabelFrame:
        """
        Cria um card para exibir dados estruturados
        
        Args:
            parent: Widget pai
            title: Título do card
            data: Dados para exibir
            row: Linha para posicionar
            column: Coluna para posicionar
            
        Returns:
            LabelFrame do card
        """
        card = ttk.LabelFrame(parent, text=title, padding="15")
        card.grid(row=row, column=column, sticky=(tk.W, tk.E), pady=10, padx=10)
        
        # Adicionar dados ao card
        data_row = 0
        
        # Nome e usuário
        if data.get('full_name'):
            ttk.Label(card, text=f"Nome: {data['full_name']}",
                     font=('Segoe UI', 10, 'bold')).grid(row=data_row, column=0, sticky=tk.W)
            data_row += 1
        
        if data.get('username'):
            ttk.Label(card, text=f"Usuário: @{data['username']}").grid(
                row=data_row, column=0, sticky=tk.W)
            data_row += 1
        
        # Estatísticas
        stats = []
        if data.get('followers_count') is not None:
            stats.append(f"Seguidores: {data['followers_count']:,}")
        if data.get('following_count') is not None:
            stats.append(f"Seguindo: {data['following_count']:,}")
        if data.get('posts_count') is not None:
            stats.append(f"Posts: {data['posts_count']:,}")
        
        if stats:
            ttk.Label(card, text=" | ".join(stats)).grid(
                row=data_row, column=0, sticky=tk.W, pady=(5, 0))
            data_row += 1
        
        # Biografia
        if data.get('biography'):
            bio_text = data['biography'][:100] + "..." if len(data['biography']) > 100 else data['biography']
            ttk.Label(card, text=f"Bio: {bio_text}", wraplength=400).grid(
                row=data_row, column=0, sticky=tk.W, pady=(5, 0))
            data_row += 1
        
        # Verificado
        if data.get('is_verified'):
            ttk.Label(card, text="✅ Verificado", foreground='blue').grid(
                row=data_row, column=0, sticky=tk.W, pady=(5, 0))
        
        return card
    
    def create_export_section(self, parent: tk.Widget, export_callback: Callable) -> Dict[str, tk.Widget]:
        """
        Cria seção de exportação com formatos e botão
        
        Args:
            parent: Widget pai
            export_callback: Função callback para exportação
            
        Returns:
            Dicionário com widgets de exportação
        """
        # Frame principal
        export_frame = ttk.LabelFrame(parent, text="Exportação de Dados", padding="15")
        
        # Status dos dados
        status_var = tk.StringVar(value="Nenhum dado disponível")
        status_label = ttk.Label(export_frame, textvariable=status_var, foreground='orange')
        status_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))
        
        # Formatos de exportação
        formats_frame = ttk.LabelFrame(export_frame, text="Formatos", padding="10")
        formats_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        format_vars = {
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
                          variable=format_vars[fmt]).grid(row=i//2, column=i%2,
                                                        sticky=tk.W, padx=10, pady=5)
        
        # Botão de exportação
        export_button = ttk.Button(export_frame, text="💾 Exportar Dados",
                                 command=export_callback, state='disabled')
        export_button.grid(row=2, column=0, pady=15)
        
        return {
            'export_frame': export_frame,
            'status_var': status_var,
            'status_label': status_label,
            'format_vars': format_vars,
            'export_button': export_button
        }
    
    def create_history_tree(self, parent: tk.Widget, columns: List[str],
                          headings: List[str]) -> ttk.Treeview:
        """
        Cria uma Treeview para exibir histórico
        
        Args:
            parent: Widget pai
            columns: Lista de colunas
            headings: Lista de cabeçalhos
            
        Returns:
            Widget Treeview
        """
        # Frame para treeview e scrollbar
        tree_frame = ttk.Frame(parent)
        
        # Treeview
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        # Configurar cabeçalhos
        for col, heading in zip(columns, headings):
            tree.heading(col, text=heading)
            tree.column(col, width=100)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar widgets
        tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar grid
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        return tree, tree_frame
    
    def create_scrollable_frame(self, parent: tk.Widget) -> tuple:
        """
        Cria um frame com scroll
        
        Args:
            parent: Widget pai
            
        Returns:
            Tupla (canvas, scrollable_frame)
        """
        # Canvas e scrollbar
        canvas = tk.Canvas(parent, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        # Configurar scroll
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        return canvas, scrollable_frame, scrollbar
    
    def show_message(self, message_type: str, title: str, message: str) -> None:
        """
        Exibe uma mensagem para o usuário
        
        Args:
            message_type: Tipo da mensagem ('info', 'warning', 'error', 'success')
            title: Título da mensagem
            message: Conteúdo da mensagem
        """
        if message_type == 'info' or message_type == 'success':
            messagebox.showinfo(title, message)
        elif message_type == 'warning':
            messagebox.showwarning(title, message)
        elif message_type == 'error':
            messagebox.showerror(title, message)
    
    def ask_confirmation(self, title: str, message: str) -> bool:
        """
        Solicita confirmação do usuário
        
        Args:
            title: Título da confirmação
            message: Mensagem de confirmação
            
        Returns:
            True se confirmado, False caso contrário
        """
        return messagebox.askyesno(title, message)
    
    def select_file(self, title: str = "Selecionar Arquivo",
                   filetypes: List[tuple] = None) -> str:
        """
        Abre diálogo para seleção de arquivo
        
        Args:
            title: Título do diálogo
            filetypes: Lista de tipos de arquivo permitidos
            
        Returns:
            Caminho do arquivo selecionado ou string vazia
        """
        if filetypes is None:
            filetypes = [("Todos os arquivos", "*.*")]
        
        return filedialog.askopenfilename(title=title, filetypes=filetypes)
    
    def select_directory(self, title: str = "Selecionar Diretório") -> str:
        """
        Abre diálogo para seleção de diretório
        
        Args:
            title: Título do diálogo
            
        Returns:
            Caminho do diretório selecionado ou string vazia
        """
        return filedialog.askdirectory(title=title)
    
    def run_in_thread(self, target_function: Callable, *args, **kwargs) -> threading.Thread:
        """
        Executa uma função em thread separada
        
        Args:
            target_function: Função para executar
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
            
        Returns:
            Thread criada
        """
        thread = threading.Thread(target=target_function, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    
    def format_number(self, number: int) -> str:
        """
        Formata um número para exibição
        
        Args:
            number: Número para formatar
            
        Returns:
            Número formatado como string
        """
        if number >= 1_000_000:
            return f"{number / 1_000_000:.1f}M"
        elif number >= 1_000:
            return f"{number / 1_000:.1f}K"
        else:
            return str(number)
    
    def format_date(self, date_obj: datetime) -> str:
        """
        Formata uma data para exibição
        
        Args:
            date_obj: Objeto datetime
            
        Returns:
            Data formatada como string
        """
        return date_obj.strftime("%d/%m/%Y %H:%M")
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        Formata tamanho de arquivo para exibição
        
        Args:
            size_bytes: Tamanho em bytes
            
        Returns:
            Tamanho formatado como string
        """
        if size_bytes >= 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
        elif size_bytes >= 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes} bytes"

class TkinterThemeManager:
    """
    Gerenciador de temas para interface Tkinter
    """
    
    def __init__(self, style: ttk.Style):
        """
        Inicializa o gerenciador de temas
        
        Args:
            style: Objeto Style do ttk
        """
        self.style = style
        self.current_theme = 'light'
        
        # Definir temas
        self.themes = {
            'light': {
                'bg': '#FFFFFF',
                'fg': '#212121',
                'select_bg': '#1565C0',
                'select_fg': '#FFFFFF',
                'accent': '#1976D2'
            },
            'dark': {
                'bg': '#2E2E2E',
                'fg': '#FFFFFF',
                'select_bg': '#1565C0',
                'select_fg': '#FFFFFF',
                'accent': '#64B5F6'
            }
        }
    
    def apply_theme(self, theme_name: str) -> None:
        """
        Aplica um tema à interface
        
        Args:
            theme_name: Nome do tema ('light' ou 'dark')
        """
        if theme_name not in self.themes:
            return
        
        theme = self.themes[theme_name]
        self.current_theme = theme_name
        
        # Configurar estilos
        self.style.configure('TLabel', background=theme['bg'], foreground=theme['fg'])
        self.style.configure('TButton', background=theme['bg'], foreground=theme['fg'])
        self.style.configure('TFrame', background=theme['bg'])
        self.style.configure('TLabelFrame', background=theme['bg'], foreground=theme['fg'])
        
        # Estilos especiais
        self.style.configure('Title.TLabel', foreground=theme['accent'])
        self.style.configure('Header.TLabel', foreground=theme['fg'])
    
    def toggle_theme(self) -> str:
        """
        Alterna entre temas claro e escuro
        
        Returns:
            Nome do tema atual
        """
        new_theme = 'dark' if self.current_theme == 'light' else 'light'
        self.apply_theme(new_theme)
        return new_theme