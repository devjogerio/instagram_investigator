#!/usr/bin/env python3
"""
Módulo de Exportação Integrado
Gerencia a exportação de dados e relatórios em múltiplos formatos
"""

import json
import csv
import os
import io
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    import base64
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class ExportManager:
    """
    Gerenciador de exportação de dados e relatórios
    """
    
    def __init__(self, export_dir: str = "exports"):
        """
        Inicializa o gerenciador de exportação
        
        Args:
            export_dir: Diretório base para exportações
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
        
        # Criar subdiretórios por formato
        for format_dir in ['json', 'csv', 'pdf', 'excel']:
            (self.export_dir / format_dir).mkdir(exist_ok=True)
    
    def export_to_json(self, data: Dict[str, Any], filename: str = None) -> str:
        """
        Exporta dados para formato JSON
        
        Args:
            data: Dados para exportar
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo exportado
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.json"
        
        if not filename.endswith('.json'):
            filename += '.json'
            
        filepath = self.export_dir / 'json' / filename
        
        # Serializar dados com tratamento de tipos especiais
        def json_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return obj.__dict__
            return str(obj)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=json_serializer)
        
        return str(filepath)
    
    def export_to_csv(self, data: Union[List[Dict], Dict[str, List]], filename: str = None) -> str:
        """
        Exporta dados para formato CSV
        
        Args:
            data: Dados para exportar (lista de dicts ou dict com listas)
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo exportado
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.csv"
        
        if not filename.endswith('.csv'):
            filename += '.csv'
            
        filepath = self.export_dir / 'csv' / filename
        
        # Converter dados para formato tabular
        if isinstance(data, dict):
            # Se é um dict, assumir que contém listas de dados
            rows = []
            max_len = max(len(v) if isinstance(v, list) else 1 for v in data.values())
            
            for i in range(max_len):
                row = {}
                for key, value in data.items():
                    if isinstance(value, list) and i < len(value):
                        row[key] = value[i]
                    elif not isinstance(value, list):
                        row[key] = value if i == 0 else ''
                    else:
                        row[key] = ''
                rows.append(row)
            data = rows
        
        if not data:
            data = [{'message': 'Nenhum dado disponível'}]
        
        # Escrever CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if data:
                fieldnames = data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
        
        return str(filepath)
    
    def export_to_excel(self, data: Dict[str, Union[List[Dict], Dict]], filename: str = None) -> str:
        """
        Exporta dados para formato Excel (requer pandas)
        
        Args:
            data: Dados para exportar (dict com sheets)
            filename: Nome do arquivo (opcional)
            
        Returns:
            Caminho do arquivo exportado
        """
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas não está disponível. Instale com: pip install pandas openpyxl")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"export_{timestamp}.xlsx"
        
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
            
        filepath = self.export_dir / 'excel' / filename
        
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, sheet_data in data.items():
                if isinstance(sheet_data, list):
                    df = pd.DataFrame(sheet_data)
                elif isinstance(sheet_data, dict):
                    df = pd.DataFrame([sheet_data])
                else:
                    df = pd.DataFrame([{'data': str(sheet_data)}])
                
                # Limitar nome da sheet a 31 caracteres (limite do Excel)
                safe_sheet_name = sheet_name[:31]
                df.to_excel(writer, sheet_name=safe_sheet_name, index=False)
        
        return str(filepath)
    
    def export_to_pdf(self, data: Dict[str, Any], filename: str = None, 
                     include_charts: bool = True) -> str:
        """
        Exporta dados para formato PDF (requer reportlab)
        
        Args:
            data: Dados para exportar
            filename: Nome do arquivo (opcional)
            include_charts: Incluir gráficos base64 no PDF
            
        Returns:
            Caminho do arquivo exportado
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab não está disponível. Instale com: pip install reportlab")
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{timestamp}.pdf"
        
        if not filename.endswith('.pdf'):
            filename += '.pdf'
            
        filepath = self.export_dir / 'pdf' / filename
        
        # Criar documento PDF
        doc = SimpleDocTemplate(str(filepath), pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        story.append(Paragraph("Relatório de Análise Cross-Platform", title_style))
        story.append(Spacer(1, 12))
        
        # Data de geração
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        story.append(Paragraph(f"Gerado em: {date_str}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Processar dados
        for section_name, section_data in data.items():
            if section_name.startswith('_'):
                continue
                
            # Título da seção
            story.append(Paragraph(section_name.replace('_', ' ').title(), styles['Heading2']))
            story.append(Spacer(1, 12))
            
            if isinstance(section_data, dict):
                # Tabela de dados
                table_data = []
                for key, value in section_data.items():
                    if key.endswith('_chart') and include_charts:
                        # Processar gráfico base64
                        try:
                            if isinstance(value, str) and value.startswith('data:image'):
                                # Extrair dados base64
                                base64_data = value.split(',')[1]
                                img_data = base64.b64decode(base64_data)
                                
                                # Criar imagem temporária
                                temp_img = io.BytesIO(img_data)
                                img = Image(temp_img, width=4*inch, height=3*inch)
                                story.append(img)
                                story.append(Spacer(1, 12))
                        except Exception:
                            # Se falhar, adicionar como texto
                            table_data.append([key.replace('_', ' ').title(), "Gráfico disponível"])
                    elif not key.endswith('_chart'):
                        # Dados textuais
                        display_value = str(value)
                        if len(display_value) > 100:
                            display_value = display_value[:100] + "..."
                        table_data.append([key.replace('_', ' ').title(), display_value])
                
                if table_data:
                    table = Table(table_data, colWidths=[2*inch, 4*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 12),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    story.append(table)
            
            elif isinstance(section_data, list):
                # Lista de itens
                for item in section_data[:10]:  # Limitar a 10 itens
                    story.append(Paragraph(f"• {str(item)}", styles['Normal']))
            else:
                # Texto simples
                story.append(Paragraph(str(section_data), styles['Normal']))
            
            story.append(Spacer(1, 20))
        
        # Construir PDF
        doc.build(story)
        
        return str(filepath)
    
    def export_comprehensive_report(self, platform_data: Dict[str, Any], 
                                  analysis_data: Dict[str, Any],
                                  visualizations: Dict[str, str] = None,
                                  formats: List[str] = None) -> Dict[str, str]:
        """
        Exporta um relatório abrangente em múltiplos formatos
        
        Args:
            platform_data: Dados das plataformas
            analysis_data: Dados de análise cross-platform
            visualizations: Gráficos em base64
            formats: Formatos para exportar ['json', 'csv', 'pdf', 'excel']
            
        Returns:
            Dict com caminhos dos arquivos exportados
        """
        if formats is None:
            formats = ['json', 'pdf']
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"comprehensive_report_{timestamp}"
        
        # Consolidar dados
        consolidated_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'platforms_analyzed': list(platform_data.keys()),
                'analysis_types': list(analysis_data.keys())
            },
            'platform_data': platform_data,
            'cross_platform_analysis': analysis_data
        }
        
        if visualizations:
            consolidated_data['visualizations'] = visualizations
        
        exported_files = {}
        
        # Exportar em cada formato solicitado
        for format_type in formats:
            try:
                if format_type == 'json':
                    filepath = self.export_to_json(consolidated_data, base_filename)
                    exported_files['json'] = filepath
                    
                elif format_type == 'csv':
                    # Para CSV, exportar dados tabulares
                    csv_data = []
                    for platform, data in platform_data.items():
                        if isinstance(data, dict):
                            row = {'platform': platform}
                            row.update({k: str(v) for k, v in data.items() if not k.endswith('_chart')})
                            csv_data.append(row)
                    
                    filepath = self.export_to_csv(csv_data, base_filename)
                    exported_files['csv'] = filepath
                    
                elif format_type == 'pdf':
                    filepath = self.export_to_pdf(consolidated_data, base_filename, 
                                                include_charts=bool(visualizations))
                    exported_files['pdf'] = filepath
                    
                elif format_type == 'excel' and PANDAS_AVAILABLE:
                    # Para Excel, criar sheets separadas
                    excel_data = {
                        'Resumo': [consolidated_data['metadata']],
                        'Análise Cross-Platform': [analysis_data] if analysis_data else []
                    }
                    
                    # Adicionar sheet para cada plataforma
                    for platform, data in platform_data.items():
                        if isinstance(data, dict):
                            excel_data[platform] = [data]
                    
                    filepath = self.export_to_excel(excel_data, base_filename)
                    exported_files['excel'] = filepath
                    
            except Exception as e:
                print(f"Erro ao exportar para {format_type}: {str(e)}")
                continue
        
        return exported_files
    
    def get_export_history(self) -> List[Dict[str, Any]]:
        """
        Retorna histórico de exportações
        
        Returns:
            Lista com informações dos arquivos exportados
        """
        history = []
        
        for format_dir in ['json', 'csv', 'pdf', 'excel']:
            format_path = self.export_dir / format_dir
            if format_path.exists():
                for file_path in format_path.glob('*'):
                    if file_path.is_file():
                        stat = file_path.stat()
                        history.append({
                            'filename': file_path.name,
                            'format': format_dir,
                            'size_bytes': stat.st_size,
                            'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            'path': str(file_path)
                        })
        
        # Ordenar por data de criação (mais recente primeiro)
        history.sort(key=lambda x: x['created_at'], reverse=True)
        return history
    
    def cleanup_old_exports(self, days_old: int = 30) -> int:
        """
        Remove exportações antigas
        
        Args:
            days_old: Idade em dias para considerar arquivo antigo
            
        Returns:
            Número de arquivos removidos
        """
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days_old)
        removed_count = 0
        
        for format_dir in ['json', 'csv', 'pdf', 'excel']:
            format_path = self.export_dir / format_dir
            if format_path.exists():
                for file_path in format_path.glob('*'):
                    if file_path.is_file():
                        file_date = datetime.fromtimestamp(file_path.stat().st_ctime)
                        if file_date < cutoff_date:
                            try:
                                file_path.unlink()
                                removed_count += 1
                            except Exception as e:
                                print(f"Erro ao remover {file_path}: {str(e)}")
        
        return removed_count