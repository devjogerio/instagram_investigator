#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Monitoramento - Instagram Investigator

Este módulo fornece monitoramento em tempo real do sistema,
alertas automáticos e notificações de problemas.

Autor: Instagram Investigator Team
Versão: 2.0.0
Data: Janeiro 2025
"""

import os
import sys
import time
import json
import smtplib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from pathlib import Path
from dataclasses import dataclass, asdict
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from collections import defaultdict, deque
import logging
import psutil

# Importar o logging manager
try:
    from .logging_manager import get_logging_manager, LoggingManager
except ImportError:
    from logging_manager import get_logging_manager, LoggingManager

# Importar configurações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logging_config import get_monitoring_config, get_performance_config


@dataclass
class Alert:
    """Estrutura para alertas do sistema"""
    id: str
    timestamp: str
    level: str  # info, warning, error, critical
    category: str  # system, api, user, security
    title: str
    message: str
    source: str
    metadata: Optional[Dict] = None
    resolved: bool = False
    resolved_at: Optional[str] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None


@dataclass
class Threshold:
    """Estrutura para limites de monitoramento"""
    metric_name: str
    warning_value: float
    critical_value: float
    comparison: str  # 'greater', 'less', 'equal'
    duration_minutes: int = 5  # Duração para considerar alerta
    enabled: bool = True


@dataclass
class NotificationChannel:
    """Canal de notificação"""
    name: str
    type: str  # email, webhook, file
    config: Dict
    enabled: bool = True
    levels: List[str] = None  # Níveis de alerta para este canal


class AlertManager:
    """Gerenciador de alertas e notificações"""
    
    def __init__(self, max_alerts: int = 1000):
        self.max_alerts = max_alerts
        self.alerts = deque(maxlen=max_alerts)
        self.active_alerts = {}  # ID -> Alert
        self.notification_channels = {}
        self.alert_callbacks = []
        self._lock = threading.Lock()
        self.logger = logging.getLogger(f"{__name__}.AlertManager")
        
        # Contadores de alertas
        self.alert_counts = defaultdict(int)
        
        # Configurar canais padrão
        self._setup_default_channels()
    
    def _setup_default_channels(self):
        """Configurar canais de notificação padrão"""
        # Canal de arquivo (sempre ativo)
        self.add_notification_channel(
            name="file",
            channel_type="file",
            config={"filepath": "logs/alerts.log"},
            levels=["warning", "error", "critical"]
        )
        
        # Canal de email (se configurado)
        email_config = self._get_email_config()
        if email_config:
            self.add_notification_channel(
                name="email",
                channel_type="email",
                config=email_config,
                levels=["error", "critical"]
            )
    
    def _get_email_config(self) -> Optional[Dict]:
        """Obter configuração de email das variáveis de ambiente"""
        smtp_server = os.getenv('ALERT_SMTP_SERVER')
        smtp_port = os.getenv('ALERT_SMTP_PORT', '587')
        smtp_user = os.getenv('ALERT_SMTP_USER')
        smtp_password = os.getenv('ALERT_SMTP_PASSWORD')
        alert_recipients = os.getenv('ALERT_RECIPIENTS')
        
        if all([smtp_server, smtp_user, smtp_password, alert_recipients]):
            return {
                'smtp_server': smtp_server,
                'smtp_port': int(smtp_port),
                'username': smtp_user,
                'password': smtp_password,
                'recipients': alert_recipients.split(','),
                'use_tls': os.getenv('ALERT_SMTP_TLS', 'true').lower() == 'true'
            }
        return None
    
    def add_notification_channel(self, name: str, channel_type: str, 
                               config: Dict, levels: List[str] = None):
        """Adicionar canal de notificação"""
        channel = NotificationChannel(
            name=name,
            type=channel_type,
            config=config,
            levels=levels or ["warning", "error", "critical"]
        )
        
        self.notification_channels[name] = channel
        self.logger.info(f"Canal de notificação adicionado: {name} ({channel_type})")
    
    def create_alert(self, level: str, category: str, title: str, 
                    message: str, source: str, metadata: Dict = None) -> str:
        """Criar novo alerta"""
        alert_id = f"{category}_{int(time.time())}_{hash(title) % 10000}"
        
        alert = Alert(
            id=alert_id,
            timestamp=datetime.now().isoformat(),
            level=level,
            category=category,
            title=title,
            message=message,
            source=source,
            metadata=metadata or {}
        )
        
        with self._lock:
            self.alerts.append(alert)
            
            # Se é crítico ou erro, manter como ativo
            if level in ['error', 'critical']:
                self.active_alerts[alert_id] = alert
            
            # Atualizar contadores
            self.alert_counts[level] += 1
            self.alert_counts[category] += 1
        
        # Enviar notificações
        self._send_notifications(alert)
        
        # Executar callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Erro em callback de alerta: {e}")
        
        self.logger.warning(f"Alerta criado: [{level.upper()}] {title}")
        return alert_id
    
    def resolve_alert(self, alert_id: str, resolved_by: str = "system"):
        """Resolver alerta ativo"""
        with self._lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.resolved = True
                alert.resolved_at = datetime.now().isoformat()
                
                # Remover dos alertas ativos
                del self.active_alerts[alert_id]
                
                self.logger.info(f"Alerta resolvido: {alert_id} por {resolved_by}")
                return True
        
        return False
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str):
        """Reconhecer alerta"""
        with self._lock:
            if alert_id in self.active_alerts:
                alert = self.active_alerts[alert_id]
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                
                self.logger.info(f"Alerta reconhecido: {alert_id} por {acknowledged_by}")
                return True
        
        return False
    
    def _send_notifications(self, alert: Alert):
        """Enviar notificações para canais configurados"""
        for channel_name, channel in self.notification_channels.items():
            if not channel.enabled:
                continue
            
            if alert.level not in channel.levels:
                continue
            
            try:
                if channel.type == "email":
                    self._send_email_notification(alert, channel)
                elif channel.type == "file":
                    self._send_file_notification(alert, channel)
                elif channel.type == "webhook":
                    self._send_webhook_notification(alert, channel)
                    
            except Exception as e:
                self.logger.error(f"Erro ao enviar notificação via {channel_name}: {e}")
    
    def _send_email_notification(self, alert: Alert, channel: NotificationChannel):
        """Enviar notificação por email"""
        config = channel.config
        
        # Criar mensagem
        msg = MIMEMultipart()
        msg['From'] = config['username']
        msg['To'] = ', '.join(config['recipients'])
        msg['Subject'] = f"[{alert.level.upper()}] Instagram Investigator - {alert.title}"
        
        # Corpo do email
        body = f"""
        Alerta do Sistema Instagram Investigator
        
        Nível: {alert.level.upper()}
        Categoria: {alert.category}
        Origem: {alert.source}
        Timestamp: {alert.timestamp}
        
        Título: {alert.title}
        
        Mensagem:
        {alert.message}
        
        Metadados:
        {json.dumps(alert.metadata, indent=2, ensure_ascii=False)}
        
        ---
        Este é um alerta automático do sistema de monitoramento.
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Enviar email
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            if config.get('use_tls', True):
                server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
        
        self.logger.debug(f"Email de alerta enviado para {len(config['recipients'])} destinatários")
    
    def _send_file_notification(self, alert: Alert, channel: NotificationChannel):
        """Enviar notificação para arquivo"""
        filepath = Path(channel.config['filepath'])
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        alert_line = f"{alert.timestamp} | {alert.level.upper()} | {alert.category} | {alert.title} | {alert.message}\n"
        
        with open(filepath, 'a', encoding='utf-8') as f:
            f.write(alert_line)
    
    def _send_webhook_notification(self, alert: Alert, channel: NotificationChannel):
        """Enviar notificação via webhook"""
        import requests
        
        config = channel.config
        payload = {
            'alert': asdict(alert),
            'system': 'instagram_investigator',
            'timestamp': datetime.now().isoformat()
        }
        
        response = requests.post(
            config['url'],
            json=payload,
            headers=config.get('headers', {}),
            timeout=config.get('timeout', 10)
        )
        
        response.raise_for_status()
        self.logger.debug(f"Webhook enviado para {config['url']}")
    
    def get_active_alerts(self, category: str = None, level: str = None) -> List[Alert]:
        """Obter alertas ativos"""
        with self._lock:
            alerts = list(self.active_alerts.values())
        
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        if level:
            alerts = [a for a in alerts if a.level == level]
        
        return sorted(alerts, key=lambda x: x.timestamp, reverse=True)
    
    def get_alert_summary(self, hours: int = 24) -> Dict:
        """Obter resumo de alertas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            recent_alerts = [
                alert for alert in self.alerts
                if datetime.fromisoformat(alert.timestamp) > cutoff_time
            ]
        
        # Contar por nível
        level_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for alert in recent_alerts:
            level_counts[alert.level] += 1
            category_counts[alert.category] += 1
        
        return {
            'period_hours': hours,
            'total_alerts': len(recent_alerts),
            'active_alerts': len(self.active_alerts),
            'by_level': dict(level_counts),
            'by_category': dict(category_counts),
            'recent_critical': [
                asdict(alert) for alert in recent_alerts
                if alert.level == 'critical'
            ][-5:]  # Últimos 5 críticos
        }
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Adicionar callback para novos alertas"""
        self.alert_callbacks.append(callback)
    
    def export_alerts(self, filepath: str, hours: int = 24):
        """Exportar alertas para arquivo"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        with self._lock:
            recent_alerts = [
                asdict(alert) for alert in self.alerts
                if datetime.fromisoformat(alert.timestamp) > cutoff_time
            ]
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'period_hours': hours,
            'total_alerts': len(recent_alerts),
            'alerts': recent_alerts,
            'summary': self.get_alert_summary(hours)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Alertas exportados para: {filepath}")


class SystemMonitor:
    """Monitor principal do sistema"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.is_monitoring = False
        self.monitor_thread = None
        self.logger = logging.getLogger(f"{__name__}.SystemMonitor")
        
        # Gerenciadores
        self.logging_manager = get_logging_manager()
        self.alert_manager = AlertManager()
        
        # Thresholds padrão
        self.thresholds = {
            'cpu_usage': Threshold('cpu_usage', 70.0, 90.0, 'greater', 5),
            'memory_usage': Threshold('memory_usage', 80.0, 95.0, 'greater', 5),
            'disk_usage': Threshold('disk_usage', 85.0, 95.0, 'greater', 10),
            'api_error_rate': Threshold('api_error_rate', 15.0, 30.0, 'greater', 3),
            'response_time': Threshold('response_time', 2.0, 5.0, 'greater', 5)
        }
        
        # Histórico de violações
        self.violation_history = defaultdict(list)
        
        # Configurar callbacks
        self._setup_callbacks()
    
    def _setup_callbacks(self):
        """Configurar callbacks de alerta"""
        def log_alert_callback(alert: Alert):
            self.logger.warning(f"Alerta: [{alert.level}] {alert.title} - {alert.message}")
        
        self.alert_manager.add_alert_callback(log_alert_callback)
    
    def start_monitoring(self):
        """Iniciar monitoramento"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="SystemMonitor"
            )
            self.monitor_thread.start()
            
            self.logger.info("Monitoramento do sistema iniciado")
            self.alert_manager.create_alert(
                level="info",
                category="system",
                title="Monitoramento Iniciado",
                message="Sistema de monitoramento foi iniciado com sucesso",
                source="SystemMonitor"
            )
    
    def stop_monitoring(self):
        """Parar monitoramento"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        
        self.logger.info("Monitoramento do sistema parado")
    
    def _monitoring_loop(self):
        """Loop principal de monitoramento"""
        while self.is_monitoring:
            try:
                self._check_system_health()
                self._check_api_health()
                self._check_application_health()
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(self.check_interval)
    
    def _check_system_health(self):
        """Verificar saúde do sistema"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            self._check_threshold('cpu_usage', cpu_percent, 'system', 'CPU')
            
            # Memória
            memory = psutil.virtual_memory()
            self._check_threshold('memory_usage', memory.percent, 'system', 'Memória')
            
            # Disco
            disk = psutil.disk_usage('/')
            self._check_threshold('disk_usage', disk.percent, 'system', 'Disco')
            
            # Processos
            process_count = len(psutil.pids())
            if process_count > 1000:
                self.alert_manager.create_alert(
                    level="warning",
                    category="system",
                    title="Alto Número de Processos",
                    message=f"Sistema executando {process_count} processos",
                    source="SystemMonitor",
                    metadata={'process_count': process_count}
                )
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar saúde do sistema: {e}")
    
    def _check_api_health(self):
        """Verificar saúde das APIs"""
        try:
            if not self.logging_manager.metrics_collector:
                return
            
            api_metrics = self.logging_manager.metrics_collector.get_api_metrics_summary()
            
            for platform, metrics in api_metrics.items():
                # Taxa de erro
                error_rate = metrics.get('error_rate', 0)
                self._check_threshold(
                    'api_error_rate', 
                    error_rate, 
                    'api', 
                    f'API {platform}',
                    metadata={'platform': platform, 'metrics': metrics}
                )
                
                # Tempo de resposta
                avg_response_time = metrics.get('avg_response_time', 0)
                self._check_threshold(
                    'response_time',
                    avg_response_time,
                    'api',
                    f'Tempo de Resposta {platform}',
                    metadata={'platform': platform, 'response_time': avg_response_time}
                )
                
        except Exception as e:
            self.logger.error(f"Erro ao verificar saúde das APIs: {e}")
    
    def _check_application_health(self):
        """Verificar saúde da aplicação"""
        try:
            # Verificar threads ativas
            active_threads = threading.active_count()
            if active_threads > 50:
                self.alert_manager.create_alert(
                    level="warning",
                    category="application",
                    title="Muitas Threads Ativas",
                    message=f"Aplicação executando {active_threads} threads",
                    source="SystemMonitor",
                    metadata={'thread_count': active_threads}
                )
            
            # Verificar arquivos de log
            log_dir = Path("logs")
            if log_dir.exists():
                total_log_size = sum(f.stat().st_size for f in log_dir.glob("*.log"))
                total_log_size_mb = total_log_size / 1024 / 1024
                
                if total_log_size_mb > 500:  # 500MB
                    self.alert_manager.create_alert(
                        level="warning",
                        category="application",
                        title="Logs Ocupando Muito Espaço",
                        message=f"Arquivos de log ocupam {total_log_size_mb:.1f}MB",
                        source="SystemMonitor",
                        metadata={'log_size_mb': total_log_size_mb}
                    )
            
        except Exception as e:
            self.logger.error(f"Erro ao verificar saúde da aplicação: {e}")
    
    def _check_threshold(self, threshold_name: str, current_value: float, 
                       category: str, resource_name: str, metadata: Dict = None):
        """Verificar se valor excede threshold"""
        threshold = self.thresholds.get(threshold_name)
        if not threshold or not threshold.enabled:
            return
        
        violation_key = f"{threshold_name}_{category}"
        current_time = datetime.now()
        
        # Verificar se há violação
        is_violation = False
        level = None
        
        if threshold.comparison == 'greater':
            if current_value >= threshold.critical_value:
                is_violation = True
                level = 'critical'
            elif current_value >= threshold.warning_value:
                is_violation = True
                level = 'warning'
        
        if is_violation:
            # Adicionar à história de violações
            self.violation_history[violation_key].append(current_time)
            
            # Manter apenas violações recentes
            cutoff_time = current_time - timedelta(minutes=threshold.duration_minutes)
            self.violation_history[violation_key] = [
                t for t in self.violation_history[violation_key] if t > cutoff_time
            ]
            
            # Verificar se deve gerar alerta (violação sustentada)
            violation_count = len(self.violation_history[violation_key])
            min_violations = max(1, threshold.duration_minutes // (self.check_interval // 60))
            
            if violation_count >= min_violations:
                self.alert_manager.create_alert(
                    level=level,
                    category=category,
                    title=f"{resource_name} - {level.title()}",
                    message=f"{resource_name} está em {current_value:.1f}% (limite: {threshold.warning_value if level == 'warning' else threshold.critical_value}%)",
                    source="SystemMonitor",
                    metadata={
                        'current_value': current_value,
                        'threshold_warning': threshold.warning_value,
                        'threshold_critical': threshold.critical_value,
                        'violation_duration_minutes': threshold.duration_minutes,
                        **(metadata or {})
                    }
                )
        else:
            # Limpar histórico se não há violação
            if violation_key in self.violation_history:
                del self.violation_history[violation_key]
    
    def add_threshold(self, name: str, warning_value: float, critical_value: float,
                    comparison: str = 'greater', duration_minutes: int = 5):
        """Adicionar threshold personalizado"""
        self.thresholds[name] = Threshold(
            metric_name=name,
            warning_value=warning_value,
            critical_value=critical_value,
            comparison=comparison,
            duration_minutes=duration_minutes
        )
        
        self.logger.info(f"Threshold adicionado: {name}")
    
    def update_threshold(self, name: str, **kwargs):
        """Atualizar threshold existente"""
        if name in self.thresholds:
            threshold = self.thresholds[name]
            
            for key, value in kwargs.items():
                if hasattr(threshold, key):
                    setattr(threshold, key, value)
            
            self.logger.info(f"Threshold atualizado: {name}")
        else:
            self.logger.warning(f"Threshold não encontrado: {name}")
    
    def get_monitoring_status(self) -> Dict:
        """Obter status do monitoramento"""
        return {
            'is_monitoring': self.is_monitoring,
            'check_interval': self.check_interval,
            'thresholds_count': len(self.thresholds),
            'active_alerts': len(self.alert_manager.active_alerts),
            'total_alerts_24h': len([
                alert for alert in self.alert_manager.alerts
                if datetime.fromisoformat(alert.timestamp) > datetime.now() - timedelta(hours=24)
            ]),
            'notification_channels': len(self.alert_manager.notification_channels),
            'uptime': self._get_uptime()
        }
    
    def _get_uptime(self) -> str:
        """Obter tempo de atividade do sistema"""
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.now() - boot_time
            
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            return f"{days}d {hours}h {minutes}m"
        except:
            return "Desconhecido"
    
    def generate_health_report(self) -> Dict:
        """Gerar relatório completo de saúde"""
        system_health = self.logging_manager.get_system_health()
        alert_summary = self.alert_manager.get_alert_summary()
        monitoring_status = self.get_monitoring_status()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_status': system_health.get('status', 'unknown'),
            'system_health': system_health,
            'alert_summary': alert_summary,
            'monitoring_status': monitoring_status,
            'active_alerts': [
                asdict(alert) for alert in self.alert_manager.get_active_alerts()
            ],
            'thresholds': {
                name: asdict(threshold) for name, threshold in self.thresholds.items()
            }
        }
    
    def export_health_report(self, filepath: str = None) -> str:
        """Exportar relatório de saúde"""
        if not filepath:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filepath = f"logs/health_report_{timestamp}.json"
        
        report = self.generate_health_report()
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Relatório de saúde exportado: {filepath}")
        return filepath
    
    def shutdown(self):
        """Finalizar monitoramento"""
        self.logger.info("Finalizando sistema de monitoramento")
        
        self.alert_manager.create_alert(
            level="info",
            category="system",
            title="Monitoramento Finalizado",
            message="Sistema de monitoramento foi finalizado",
            source="SystemMonitor"
        )
        
        self.stop_monitoring()


# Instância global do monitor
_system_monitor = None


def get_system_monitor() -> SystemMonitor:
    """Obter instância global do monitor do sistema"""
    global _system_monitor
    if _system_monitor is None:
        _system_monitor = SystemMonitor()
    return _system_monitor


def setup_monitoring(check_interval: Optional[int] = None) -> SystemMonitor:
    """
    Configura o sistema de monitoramento usando configurações do arquivo de configuração
    
    Args:
        check_interval: Intervalo entre verificações em segundos (opcional, usa configuração padrão)
    
    Returns:
        Instância do SystemMonitor configurado
    """
    global _system_monitor
    
    # Obter configurações
    config = get_monitoring_config()
    
    # Usar parâmetro fornecido ou configuração padrão
    check_interval = check_interval or config.get('check_interval', 30)
    
    _system_monitor = SystemMonitor(check_interval=check_interval)
    return _system_monitor


if __name__ == "__main__":
    # Teste do sistema de monitoramento
    import time
    
    # Configurar logging
    from logging_manager import setup_logging
    setup_logging(log_level="DEBUG")
    
    # Configurar monitoramento
    monitor = setup_monitoring(check_interval=10)
    
    # Iniciar monitoramento
    monitor.start_monitoring()
    
    # Simular alguns alertas
    monitor.alert_manager.create_alert(
        level="warning",
        category="test",
        title="Teste de Alerta",
        message="Este é um alerta de teste",
        source="TestScript"
    )
    
    # Aguardar alguns ciclos
    time.sleep(30)
    
    # Gerar relatório
    report_file = monitor.export_health_report()
    print(f"Relatório gerado: {report_file}")
    
    # Finalizar
    monitor.shutdown()