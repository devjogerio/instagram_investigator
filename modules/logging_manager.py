#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Logging e Monitoramento - Instagram Investigator

Este módulo fornece funcionalidades avançadas de logging, monitoramento
e coleta de métricas para a aplicação.

Autor: Instagram Investigator Team
Versão: 2.0.0
Data: Janeiro 2025
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import psutil

# Importar configurações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logging_config import get_logging_config, get_monitoring_config, get_performance_config


@dataclass
class LogEntry:
    """Estrutura para entrada de log estruturado"""
    timestamp: str
    level: str
    module: str
    function: str
    message: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    platform: Optional[str] = None
    duration: Optional[float] = None
    error_code: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class PerformanceMetric:
    """Estrutura para métricas de performance"""
    timestamp: str
    metric_name: str
    value: float
    unit: str
    tags: Optional[Dict[str, str]] = None


@dataclass
class SystemMetrics:
    """Estrutura para métricas do sistema"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    disk_usage_percent: float
    network_sent_mb: float
    network_recv_mb: float
    active_threads: int


class CustomFormatter(logging.Formatter):
    """Formatter personalizado com cores e estrutura melhorada"""
    
    # Códigos de cor ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # Ciano
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarelo
        'ERROR': '\033[31m',      # Vermelho
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def __init__(self, use_colors: bool = True, include_thread: bool = True):
        self.use_colors = use_colors
        self.include_thread = include_thread
        
        # Formato base
        fmt = '%(asctime)s | %(levelname)-8s | %(name)-20s'
        
        if include_thread:
            fmt += ' | %(thread)d'
            
        fmt += ' | %(funcName)-15s | %(message)s'
        
        super().__init__(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record):
        """Formatar registro de log com cores opcionais"""
        if self.use_colors and hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            # Aplicar cores apenas se o terminal suportar
            level_color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
            record.levelname = f"{level_color}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class MetricsCollector:
    """Coletor de métricas de sistema e aplicação"""
    
    def __init__(self, collection_interval: int = 60):
        self.collection_interval = collection_interval
        self.metrics_history = deque(maxlen=1440)  # 24 horas de dados (1 min intervals)
        self.performance_metrics = defaultdict(list)
        self.api_metrics = defaultdict(lambda: {'calls': 0, 'errors': 0, 'total_time': 0})
        self.user_actions = defaultdict(int)
        self.is_collecting = False
        self.collection_thread = None
        self._lock = threading.Lock()
        
        # Métricas de rede iniciais
        self.initial_network = psutil.net_io_counters()
    
    def start_collection(self):
        """Iniciar coleta automática de métricas"""
        if not self.is_collecting:
            self.is_collecting = True
            self.collection_thread = threading.Thread(
                target=self._collect_loop,
                daemon=True,
                name="MetricsCollector"
            )
            self.collection_thread.start()
            logging.info("Coleta de métricas iniciada")
    
    def stop_collection(self):
        """Parar coleta de métricas"""
        self.is_collecting = False
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        logging.info("Coleta de métricas parada")
    
    def _collect_loop(self):
        """Loop principal de coleta de métricas"""
        while self.is_collecting:
            try:
                self._collect_system_metrics()
                time.sleep(self.collection_interval)
            except Exception as e:
                logging.error(f"Erro na coleta de métricas: {e}")
                time.sleep(self.collection_interval)
    
    def _collect_system_metrics(self):
        """Coletar métricas do sistema"""
        try:
            # Métricas de CPU e memória
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Métricas de rede
            current_network = psutil.net_io_counters()
            network_sent_mb = (current_network.bytes_sent - self.initial_network.bytes_sent) / 1024 / 1024
            network_recv_mb = (current_network.bytes_recv - self.initial_network.bytes_recv) / 1024 / 1024
            
            # Número de threads ativas
            active_threads = threading.active_count()
            
            # Criar métrica do sistema
            system_metric = SystemMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                memory_used_mb=memory.used / 1024 / 1024,
                disk_usage_percent=disk.percent,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                active_threads=active_threads
            )
            
            with self._lock:
                self.metrics_history.append(system_metric)
            
        except Exception as e:
            logging.error(f"Erro ao coletar métricas do sistema: {e}")
    
    def record_api_call(self, platform: str, success: bool, duration: float):
        """Registrar chamada de API"""
        with self._lock:
            self.api_metrics[platform]['calls'] += 1
            self.api_metrics[platform]['total_time'] += duration
            
            if not success:
                self.api_metrics[platform]['errors'] += 1
    
    def record_user_action(self, action: str):
        """Registrar ação do usuário"""
        with self._lock:
            self.user_actions[action] += 1
    
    def record_performance_metric(self, name: str, value: float, unit: str, tags: Dict[str, str] = None):
        """Registrar métrica de performance personalizada"""
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            metric_name=name,
            value=value,
            unit=unit,
            tags=tags or {}
        )
        
        with self._lock:
            self.performance_metrics[name].append(metric)
            
            # Manter apenas últimas 1000 métricas por tipo
            if len(self.performance_metrics[name]) > 1000:
                self.performance_metrics[name] = self.performance_metrics[name][-1000:]
    
    def get_system_metrics_summary(self, hours: int = 1) -> Dict:
        """Obter resumo das métricas do sistema"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            recent_metrics = [
                m for m in self.metrics_history
                if datetime.fromisoformat(m.timestamp) > cutoff_time
            ]
        
        if not recent_metrics:
            return {}
        
        # Calcular estatísticas
        cpu_values = [m.cpu_percent for m in recent_metrics]
        memory_values = [m.memory_percent for m in recent_metrics]
        
        return {
            'period_hours': hours,
            'samples_count': len(recent_metrics),
            'cpu': {
                'avg': sum(cpu_values) / len(cpu_values),
                'max': max(cpu_values),
                'min': min(cpu_values)
            },
            'memory': {
                'avg': sum(memory_values) / len(memory_values),
                'max': max(memory_values),
                'min': min(memory_values)
            },
            'latest': asdict(recent_metrics[-1]) if recent_metrics else None
        }
    
    def get_api_metrics_summary(self) -> Dict:
        """Obter resumo das métricas de API"""
        with self._lock:
            summary = {}
            for platform, metrics in self.api_metrics.items():
                calls = metrics['calls']
                errors = metrics['errors']
                total_time = metrics['total_time']
                
                summary[platform] = {
                    'total_calls': calls,
                    'total_errors': errors,
                    'error_rate': (errors / calls * 100) if calls > 0 else 0,
                    'avg_response_time': (total_time / calls) if calls > 0 else 0,
                    'success_rate': ((calls - errors) / calls * 100) if calls > 0 else 0
                }
            
            return summary
    
    def export_metrics(self, filepath: str):
        """Exportar métricas para arquivo JSON"""
        with self._lock:
            data = {
                'export_timestamp': datetime.now().isoformat(),
                'system_metrics': [asdict(m) for m in self.metrics_history],
                'api_metrics': dict(self.api_metrics),
                'user_actions': dict(self.user_actions),
                'performance_metrics': {
                    name: [asdict(m) for m in metrics]
                    for name, metrics in self.performance_metrics.items()
                }
            }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Métricas exportadas para: {filepath}")


class LoggingManager:
    """Gerenciador principal de logging e monitoramento"""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 log_level: str = "INFO",
                 max_file_size: int = 10 * 1024 * 1024,  # 10MB
                 backup_count: int = 5,
                 enable_console: bool = True,
                 enable_metrics: bool = True):
        
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper())
        self.max_file_size = max_file_size
        self.backup_count = backup_count
        self.enable_console = enable_console
        self.enable_metrics = enable_metrics
        
        # Criar diretório de logs
        self.log_dir.mkdir(exist_ok=True)
        
        # Inicializar coletor de métricas
        self.metrics_collector = MetricsCollector() if enable_metrics else None
        
        # Configurar logging
        self._setup_logging()
        
        # Logger principal
        self.logger = logging.getLogger('instagram_investigator')
        
        # Registrar início do sistema
        self.logger.info("Sistema de logging inicializado")
        
        if self.metrics_collector:
            self.metrics_collector.start_collection()
    
    def _setup_logging(self):
        """Configurar sistema de logging"""
        # Configuração raiz
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remover handlers existentes
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)
        
        # Formatter para arquivos (sem cores)
        file_formatter = CustomFormatter(use_colors=False, include_thread=True)
        
        # Handler para arquivo principal (rotativo por tamanho)
        main_file_handler = RotatingFileHandler(
            filename=self.log_dir / "app.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        main_file_handler.setLevel(self.log_level)
        main_file_handler.setFormatter(file_formatter)
        root_logger.addHandler(main_file_handler)
        
        # Handler para erros (rotativo por tempo)
        error_file_handler = TimedRotatingFileHandler(
            filename=self.log_dir / "errors.log",
            when='midnight',
            interval=1,
            backupCount=30,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_file_handler)
        
        # Handler para console (com cores)
        if self.enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_formatter = CustomFormatter(use_colors=True, include_thread=False)
            console_handler.setFormatter(console_formatter)
            root_logger.addHandler(console_handler)
        
        # Handler para métricas de API (arquivo separado)
        api_file_handler = RotatingFileHandler(
            filename=self.log_dir / "api_calls.log",
            maxBytes=self.max_file_size,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        api_file_handler.setLevel(logging.INFO)
        api_file_handler.setFormatter(file_formatter)
        
        # Logger específico para APIs
        api_logger = logging.getLogger('api_calls')
        api_logger.addHandler(api_file_handler)
        api_logger.setLevel(logging.INFO)
        api_logger.propagate = False
    
    def log_api_call(self, platform: str, endpoint: str, success: bool, 
                     duration: float, response_size: int = None, 
                     error_message: str = None, user_id: str = None):
        """Registrar chamada de API com métricas"""
        
        # Log estruturado
        log_data = {
            'platform': platform,
            'endpoint': endpoint,
            'success': success,
            'duration_ms': round(duration * 1000, 2),
            'response_size_bytes': response_size,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id
        }
        
        if error_message:
            log_data['error'] = error_message
        
        # Log para arquivo de APIs
        api_logger = logging.getLogger('api_calls')
        api_logger.info(json.dumps(log_data, ensure_ascii=False))
        
        # Registrar métricas
        if self.metrics_collector:
            self.metrics_collector.record_api_call(platform, success, duration)
        
        # Log principal
        status = "SUCCESS" if success else "ERROR"
        message = f"API {platform} | {endpoint} | {status} | {duration*1000:.1f}ms"
        
        if success:
            self.logger.info(message)
        else:
            self.logger.error(f"{message} | {error_message}")
    
    def log_user_action(self, action: str, user_id: str = None, 
                       session_id: str = None, metadata: Dict = None):
        """Registrar ação do usuário"""
        
        log_data = {
            'action': action,
            'user_id': user_id,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.logger.info(f"USER_ACTION | {action} | {json.dumps(log_data, ensure_ascii=False)}")
        
        # Registrar métrica
        if self.metrics_collector:
            self.metrics_collector.record_user_action(action)
    
    def log_performance(self, operation: str, duration: float, 
                       success: bool = True, metadata: Dict = None):
        """Registrar métrica de performance"""
        
        log_data = {
            'operation': operation,
            'duration_ms': round(duration * 1000, 2),
            'success': success,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.logger.info(f"PERFORMANCE | {operation} | {json.dumps(log_data, ensure_ascii=False)}")
        
        # Registrar métrica
        if self.metrics_collector:
            self.metrics_collector.record_performance_metric(
                name=operation,
                value=duration,
                unit='seconds',
                tags={'success': str(success)}
            )
    
    def get_system_health(self) -> Dict:
        """Obter status de saúde do sistema"""
        health = {
            'timestamp': datetime.now().isoformat(),
            'status': 'healthy',
            'issues': []
        }
        
        if self.metrics_collector:
            # Métricas do sistema
            system_metrics = self.metrics_collector.get_system_metrics_summary(hours=1)
            
            if system_metrics:
                # Verificar CPU
                if system_metrics['cpu']['avg'] > 80:
                    health['issues'].append('High CPU usage detected')
                    health['status'] = 'warning'
                
                # Verificar memória
                if system_metrics['memory']['avg'] > 85:
                    health['issues'].append('High memory usage detected')
                    health['status'] = 'warning'
                
                health['system_metrics'] = system_metrics
            
            # Métricas de API
            api_metrics = self.metrics_collector.get_api_metrics_summary()
            
            for platform, metrics in api_metrics.items():
                if metrics['error_rate'] > 20:
                    health['issues'].append(f'High error rate for {platform} API: {metrics["error_rate"]:.1f}%')
                    health['status'] = 'warning'
            
            health['api_metrics'] = api_metrics
        
        # Se há problemas críticos
        if len(health['issues']) > 5:
            health['status'] = 'critical'
        
        return health
    
    def export_logs_summary(self, hours: int = 24) -> str:
        """Exportar resumo dos logs"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_file = self.log_dir / f"logs_summary_{timestamp}.json"
        
        summary = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'period_hours': hours,
                'generated_by': 'LoggingManager'
            },
            'system_health': self.get_system_health()
        }
        
        # Exportar métricas se disponível
        if self.metrics_collector:
            metrics_file = self.log_dir / f"metrics_{timestamp}.json"
            self.metrics_collector.export_metrics(str(metrics_file))
            summary['metrics_file'] = str(metrics_file)
        
        # Salvar resumo
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Resumo de logs exportado: {export_file}")
        return str(export_file)
    
    def cleanup_old_logs(self, days: int = 30):
        """Limpar logs antigos"""
        cutoff_date = datetime.now() - timedelta(days=days)
        cleaned_files = 0
        
        for log_file in self.log_dir.glob("*.log*"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    cleaned_files += 1
            except Exception as e:
                self.logger.warning(f"Erro ao limpar arquivo {log_file}: {e}")
        
        self.logger.info(f"Limpeza concluída: {cleaned_files} arquivos removidos")
    
    def shutdown(self):
        """Finalizar sistema de logging"""
        self.logger.info("Finalizando sistema de logging")
        
        if self.metrics_collector:
            self.metrics_collector.stop_collection()
        
        # Forçar flush de todos os handlers
        for handler in logging.getLogger().handlers:
            handler.flush()
        
        logging.shutdown()


# Decorador para logging automático de funções
def log_function_call(logger_name: str = None):
    """Decorador para logging automático de chamadas de função"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = logging.getLogger(logger_name or func.__module__)
            start_time = time.time()
            
            try:
                logger.debug(f"Iniciando {func.__name__} com args={len(args)}, kwargs={len(kwargs)}")
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                logger.debug(f"Concluído {func.__name__} em {duration:.3f}s")
                return result
                
            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Erro em {func.__name__} após {duration:.3f}s: {e}")
                raise
        
        return wrapper
    return decorator


# Instância global do gerenciador de logging
_logging_manager = None


def get_logging_manager() -> LoggingManager:
    """Obter instância global do gerenciador de logging"""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager


def setup_logging(log_dir: Optional[str] = None, log_level: Optional[str] = None, 
                 enable_metrics: Optional[bool] = None) -> LoggingManager:
    """Configurar sistema de logging global usando configurações do arquivo de configuração"""
    global _logging_manager
    
    # Obter configurações
    config = get_logging_config()
    
    # Usar parâmetros fornecidos ou configurações padrão
    log_dir = log_dir or config['log_directory']
    log_level = log_level or config['default_level']
    enable_metrics = enable_metrics if enable_metrics is not None else config['metrics']['enabled']
    
    _logging_manager = LoggingManager(
        log_dir=log_dir,
        log_level=log_level,
        enable_metrics=enable_metrics
    )
    return _logging_manager


if __name__ == "__main__":
    # Teste do sistema de logging
    logging_manager = setup_logging(log_level="DEBUG")
    
    logger = logging.getLogger(__name__)
    
    # Teste de logs básicos
    logger.debug("Teste de debug")
    logger.info("Teste de info")
    logger.warning("Teste de warning")
    logger.error("Teste de error")
    
    # Teste de métricas
    logging_manager.log_api_call(
        platform="instagram",
        endpoint="/user/info",
        success=True,
        duration=0.5,
        response_size=1024
    )
    
    logging_manager.log_user_action(
        action="search_user",
        user_id="test_user",
        metadata={"platform": "instagram", "query": "test"}
    )
    
    # Aguardar coleta de métricas
    time.sleep(2)
    
    # Exibir saúde do sistema
    health = logging_manager.get_system_health()
    print(json.dumps(health, indent=2, ensure_ascii=False))
    
    # Finalizar
    logging_manager.shutdown()