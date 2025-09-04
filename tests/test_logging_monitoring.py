#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para Sistema de Logging e Monitoramento

Este módulo contém testes para verificar o funcionamento correto
dos sistemas de logging e monitoramento.

Autor: Instagram Investigator Team
Versão: 2.0.0
"""

import pytest
import tempfile
import time
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Adicionar o diretório pai ao path para importações
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.logging_manager import (
    LoggingManager, setup_logging, get_logging_manager,
    LogEntry, PerformanceMetric, SystemMetrics, log_function_call
)
from modules.system_monitor import (
    SystemMonitor, setup_monitoring, get_system_monitor,
    Alert, Threshold, NotificationChannel
)
from config.logging_config import (
    get_logging_config, get_monitoring_config, get_performance_config
)

class TestLoggingManager:
    """Testes para o LoggingManager"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        self.log_dir.mkdir(exist_ok=True)
    
    def test_logging_manager_initialization(self):
        """Testa a inicialização do LoggingManager"""
        manager = LoggingManager(str(self.log_dir), enable_metrics=True)
        
        assert str(manager.log_dir) == str(self.log_dir)
        assert manager.enable_metrics is True
        assert manager.metrics_collector is not None
    
    def test_log_entry_creation(self):
        """Testa a criação de entradas de log"""
        manager = LoggingManager(str(self.log_dir))
        
        # Testar log de ação do usuário
        manager.log_user_action(
            "test_action",
            metadata={"test_key": "test_value"}
        )
        
        # Verificar se o log foi criado
        log_files = list(self.log_dir.glob("*.log"))
        assert len(log_files) > 0
    
    def test_api_call_logging(self):
        """Testa o logging de chamadas de API"""
        manager = LoggingManager(str(self.log_dir))
        
        # Simular chamada de API
        manager.log_api_call(
            platform="instagram",
            endpoint="/users/profile",
            success=True,
            duration=0.5,
            response_size=1024,
            error_message=None,
            user_id="test_user"
        )
        
        # Verificar se o log foi criado
        api_log_file = self.log_dir / "api_calls.log"
        assert api_log_file.exists()
    
    def test_performance_logging(self):
        """Testa o logging de métricas de performance"""
        manager = LoggingManager(str(self.log_dir), enable_metrics=True)
        
        # Testar log de performance
        manager.log_performance(
            "test_operation",
            1.5,
            50 * 1024 * 1024,  # 50MB
            metadata={"records_processed": 100}
        )
        
        # Verificar se as métricas foram coletadas
        assert len(manager.metrics_collector.performance_metrics) > 0
    
    def test_logging_decorator(self):
        """Testa o decorador de logging"""
        manager = LoggingManager(str(self.log_dir))
        
        @log_function_call()
        def test_function(x, y):
            time.sleep(0.1)  # Simular processamento
            return x + y
        
        result = test_function(2, 3)
        assert result == 5
        
        # Verificar se o log da função foi criado
        log_files = list(self.log_dir.glob("*.log"))
        assert len(log_files) > 0

class TestSystemMonitor:
    """Testes para o SystemMonitor"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_system_monitor_initialization(self):
        """Testa a inicialização do monitor do sistema"""
        monitor = SystemMonitor(check_interval=10)
        
        assert monitor.check_interval == 10
        assert not monitor.is_monitoring
        assert monitor.alert_manager is not None
    
    def test_threshold_creation(self):
        """Testa a criação de limites de alerta"""
        threshold = Threshold(
            metric_name="cpu_usage",
            warning_value=70.0,
            critical_value=90.0,
            comparison="greater"
        )
        
        assert threshold.metric_name == "cpu_usage"
        assert threshold.warning_value == 70.0
        assert threshold.critical_value == 90.0
        assert threshold.comparison == "greater"
    
    def test_alert_creation(self):
        """Testa a criação de alertas"""
        alert = Alert(
            id="alert_001",
            timestamp="2025-01-03T10:00:00",
            level="warning",
            category="system",
            title="High CPU Usage",
            message="CPU usage is high",
            source="SystemMonitor",
            metadata={"cpu_percent": 85.0}
        )
        
        assert alert.id == "alert_001"
        assert alert.level == "warning"
        assert alert.category == "system"
        assert "CPU usage" in alert.message
    
    def test_notification_channel(self):
        """Testa os canais de notificação"""
        channel = NotificationChannel(
            name="test_console",
            type="console",
            config={"min_severity": "medium"}
        )
        
        assert channel.name == "test_console"
        assert channel.type == "console"
        assert channel.config["min_severity"] == "medium"
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_system_health_check(self, mock_memory, mock_cpu):
        """Testa a verificação de saúde do sistema"""
        # Configurar mocks
        mock_cpu.return_value = 75.0
        mock_memory.return_value = MagicMock(percent=70.0)
        
        monitor = SystemMonitor(check_interval=1)
        health_report = monitor.generate_health_report()
        
        assert "timestamp" in health_report
        assert "overall_status" in health_report
        assert "system_health" in health_report
        assert "alert_summary" in health_report

class TestConfiguration:
    """Testes para as configurações"""
    
    def test_logging_config(self):
        """Testa a obtenção das configurações de logging"""
        config = get_logging_config()
        
        assert "log_directory" in config
        assert "default_level" in config
        assert "loggers" in config
        assert "metrics" in config
    
    def test_monitoring_config(self):
        """Testa a obtenção das configurações de monitoramento"""
        config = get_monitoring_config()
        
        assert "check_interval" in config
        assert "thresholds" in config
        assert "alerts" in config
        assert "notification_channels" in config
    
    def test_performance_config(self):
        """Testa a obtenção das configurações de performance"""
        config = get_performance_config()
        
        assert "limits" in config
        assert "cache" in config
        assert "rate_limiting" in config

class TestIntegration:
    """Testes de integração"""
    
    def setup_method(self):
        """Configuração para cada teste"""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_setup_functions(self):
        """Testa as funções de configuração global"""
        # Testar setup de logging
        logging_manager = setup_logging(log_dir=self.temp_dir)
        assert logging_manager is not None
        assert get_logging_manager() is not None
        
        # Testar setup de monitoramento
        system_monitor = setup_monitoring(check_interval=5)
        assert system_monitor is not None
        assert get_system_monitor() is not None
    
    def test_logging_and_monitoring_integration(self):
        """Testa a integração entre logging e monitoramento"""
        # Configurar sistemas
        logging_manager = setup_logging(log_dir=self.temp_dir)
        system_monitor = setup_monitoring(check_interval=1)
        
        # Simular atividade
        logging_manager.log_user_action("test_integration")
        
        # Verificar se ambos os sistemas estão funcionando
        assert logging_manager is not None
        assert system_monitor is not None
        
        # Verificar se os logs foram criados
        log_files = list(Path(self.temp_dir).glob("*.log"))
        assert len(log_files) > 0

if __name__ == "__main__":
    # Executar testes se o arquivo for executado diretamente
    pytest.main([__file__, "-v"])