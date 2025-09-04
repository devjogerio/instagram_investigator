#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração do Sistema de Logging

Este módulo contém as configurações para o sistema de logging e monitoramento
do Instagram Investigator.

Autor: Instagram Investigator Team
Versão: 2.0.0
"""

import os
from typing import Dict, Any
from pathlib import Path

# Configurações de Logging
LOGGING_CONFIG = {
    # Diretório base para logs
    'log_directory': 'logs',
    
    # Nível de logging padrão
    'default_level': 'INFO',
    
    # Formato das mensagens de log
    'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    
    # Formato de data/hora
    'date_format': '%Y-%m-%d %H:%M:%S',
    
    # Configurações de rotação de arquivos
    'rotation': {
        'max_bytes': 10 * 1024 * 1024,  # 10MB
        'backup_count': 5,
        'encoding': 'utf-8'
    },
    
    # Configurações específicas por logger
    'loggers': {
        'app': {
            'level': 'INFO',
            'filename': 'app.log',
            'console': True
        },
        'api': {
            'level': 'DEBUG',
            'filename': 'api.log',
            'console': False
        },
        'performance': {
            'level': 'INFO',
            'filename': 'performance.log',
            'console': False
        },
        'security': {
            'level': 'WARNING',
            'filename': 'security.log',
            'console': True
        },
        'user_actions': {
            'level': 'INFO',
            'filename': 'user_actions.log',
            'console': False
        }
    },
    
    # Configurações de métricas
    'metrics': {
        'enabled': True,
        'collection_interval': 30,  # segundos
        'retention_days': 30,
        'export_format': 'json'
    }
}

# Configurações de Monitoramento
MONITORING_CONFIG = {
    # Intervalo de verificação do sistema (segundos)
    'check_interval': 60,
    
    # Limites de alerta
    'thresholds': {
        'cpu_usage': 80.0,  # %
        'memory_usage': 85.0,  # %
        'disk_usage': 90.0,  # %
        'api_response_time': 5.0,  # segundos
        'error_rate': 10.0,  # %
        'concurrent_requests': 50
    },
    
    # Configurações de alertas
    'alerts': {
        'enabled': True,
        'cooldown_minutes': 15,  # Tempo mínimo entre alertas do mesmo tipo
        'max_alerts_per_hour': 10,
        'severity_levels': ['low', 'medium', 'high', 'critical']
    },
    
    # Canais de notificação
    'notification_channels': {
        'console': {
            'enabled': True,
            'min_severity': 'medium'
        },
        'file': {
            'enabled': True,
            'filename': 'alerts.log',
            'min_severity': 'low'
        },
        'email': {
            'enabled': False,  # Configurar via .env
            'min_severity': 'high',
            'smtp_server': None,  # Configurar via .env
            'smtp_port': 587,
            'recipients': []  # Configurar via .env
        }
    },
    
    # Métricas de saúde do sistema
    'health_checks': {
        'system_resources': True,
        'api_endpoints': True,
        'database_connection': False,  # Não aplicável neste projeto
        'external_services': True,
        'file_system': True
    }
}

# Configurações de Performance
PERFORMANCE_CONFIG = {
    # Limites de performance
    'limits': {
        'max_search_time': 300,  # 5 minutos
        'max_export_time': 180,  # 3 minutos
        'max_analysis_time': 120,  # 2 minutos
        'max_memory_per_operation': 500 * 1024 * 1024,  # 500MB
    },
    
    # Configurações de cache
    'cache': {
        'enabled': True,
        'ttl_seconds': 3600,  # 1 hora
        'max_size_mb': 100,
        'cleanup_interval': 1800  # 30 minutos
    },
    
    # Configurações de rate limiting
    'rate_limiting': {
        'enabled': True,
        'requests_per_minute': 60,
        'burst_limit': 10
    }
}

def get_logging_config() -> Dict[str, Any]:
    """
    Retorna a configuração de logging, aplicando variáveis de ambiente se disponíveis
    
    Returns:
        Dict com configurações de logging
    """
    config = LOGGING_CONFIG.copy()
    
    # Aplicar configurações do ambiente
    if os.getenv('LOG_LEVEL'):
        config['default_level'] = os.getenv('LOG_LEVEL')
    
    if os.getenv('LOG_DIRECTORY'):
        config['log_directory'] = os.getenv('LOG_DIRECTORY')
    
    # Criar diretório de logs se não existir
    log_dir = Path(config['log_directory'])
    log_dir.mkdir(exist_ok=True)
    
    return config

def get_monitoring_config() -> Dict[str, Any]:
    """
    Retorna a configuração de monitoramento, aplicando variáveis de ambiente se disponíveis
    
    Returns:
        Dict com configurações de monitoramento
    """
    config = MONITORING_CONFIG.copy()
    
    # Aplicar configurações do ambiente
    if os.getenv('MONITORING_INTERVAL'):
        try:
            config['check_interval'] = int(os.getenv('MONITORING_INTERVAL'))
        except ValueError:
            pass
    
    if os.getenv('ALERT_EMAIL_ENABLED', '').lower() == 'true':
        config['notification_channels']['email']['enabled'] = True
        config['notification_channels']['email']['smtp_server'] = os.getenv('SMTP_SERVER')
        
        recipients = os.getenv('ALERT_EMAIL_RECIPIENTS', '')
        if recipients:
            config['notification_channels']['email']['recipients'] = [
                email.strip() for email in recipients.split(',')
            ]
    
    return config

def get_performance_config() -> Dict[str, Any]:
    """
    Retorna a configuração de performance, aplicando variáveis de ambiente se disponíveis
    
    Returns:
        Dict com configurações de performance
    """
    config = PERFORMANCE_CONFIG.copy()
    
    # Aplicar configurações do ambiente
    if os.getenv('CACHE_ENABLED', '').lower() == 'false':
        config['cache']['enabled'] = False
    
    if os.getenv('RATE_LIMITING_ENABLED', '').lower() == 'false':
        config['rate_limiting']['enabled'] = False
    
    return config

# Configurações de desenvolvimento vs produção
def get_environment_config() -> Dict[str, Any]:
    """
    Retorna configurações específicas do ambiente (dev/prod)
    
    Returns:
        Dict com configurações do ambiente
    """
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    if env == 'production':
        return {
            'logging': {
                'default_level': 'WARNING',
                'console_output': False,
                'detailed_errors': False
            },
            'monitoring': {
                'check_interval': 30,
                'alerts_enabled': True
            },
            'performance': {
                'cache_enabled': True,
                'rate_limiting_enabled': True
            }
        }
    else:  # development
        return {
            'logging': {
                'default_level': 'DEBUG',
                'console_output': True,
                'detailed_errors': True
            },
            'monitoring': {
                'check_interval': 120,
                'alerts_enabled': False
            },
            'performance': {
                'cache_enabled': False,
                'rate_limiting_enabled': False
            }
        }