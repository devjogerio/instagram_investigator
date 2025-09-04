#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para extração de dados do Instagram
"""

import time
import logging
from .instagram_api import InstagramAPI

logger = logging.getLogger(__name__)


class DataExtractor:
    """Classe para extração de dados do Instagram"""
    
    def __init__(self, session_id):
        """Inicializa o extrator com o session ID fornecido"""
        self.api = InstagramAPI(session_id)
    
    def investigate_profile(self, username):
        """Executa investigação completa do perfil"""
        try:
            # Passo 1: Obter ID do usuário
            logger.info(f"Obtendo ID do usuário: {username}")
            user_id_data = self.api.get_user_id(username)
            
            if user_id_data.get("error"):
                logger.error(f"Erro ao obter ID: {user_id_data['error']}")
                raise Exception(user_id_data["error"])
            
            user_id = user_id_data["id"]
            logger.info(f"ID encontrado: {user_id}")
            
            # Pequeno delay para evitar rate limiting
            time.sleep(1)
            
            # Passo 2: Obter informações detalhadas
            logger.info("Coletando informações detalhadas")
            info_data = self.api.get_user_info(user_id)
            
            if info_data.get("error"):
                logger.error(f"Erro ao obter informações: {info_data['error']}")
                raise Exception(info_data["error"])
            
            user_info = info_data["user"]
            logger.info("Informações básicas coletadas")
            
            # Pequeno delay para evitar rate limiting
            time.sleep(1)
            
            # Passo 3: Lookup avançado
            logger.info("Realizando lookup avançado")
            advanced_data = self.api.advanced_lookup(username)
            
            if not advanced_data.get("error"):
                logger.info("Lookup avançado concluído")
            else:
                logger.warning(f"Lookup avançado falhou: {advanced_data.get('error')}")
            
            # Combina dados
            combined_data = {**user_info}
            
            # Adiciona dados do lookup avançado se disponíveis
            if advanced_data.get("user"):
                combined_data.update(advanced_data.get("user", {}))
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Falha na investigação: {str(e)}")
            raise Exception(f"Falha na investigação: {str(e)}")