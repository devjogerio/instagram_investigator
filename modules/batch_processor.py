#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para processamento em lote de múltiplos perfis do Instagram
"""

import time
import logging
import threading
from queue import Queue
from datetime import datetime

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Classe para processamento em lote de múltiplos perfis do Instagram"""
    
    def __init__(self, data_extractor, max_concurrent=2, delay_between_requests=2):
        """Inicializa o processador em lote
        
        Args:
            data_extractor: Instância de DataExtractor para extrair dados
            max_concurrent: Número máximo de requisições concorrentes
            delay_between_requests: Atraso entre requisições (em segundos)
        """
        self.data_extractor = data_extractor
        self.max_concurrent = max_concurrent
        self.delay = delay_between_requests
        self.results = {}
        self.errors = {}
        self.queue = Queue()
        self.lock = threading.Lock()
        self.stop_event = threading.Event()
        self.workers = []
        self.progress_callback = None
        self.completion_callback = None
    
    def set_callbacks(self, progress_callback=None, completion_callback=None):
        """Define callbacks para acompanhamento do progresso
        
        Args:
            progress_callback: Função chamada quando um perfil é processado
                               Recebe (username, success, current, total)
            completion_callback: Função chamada quando todo o lote é concluído
                                Recebe (results, errors)
        """
        self.progress_callback = progress_callback
        self.completion_callback = completion_callback
    
    def add_profile(self, username):
        """Adiciona um perfil à fila de processamento
        
        Args:
            username: Nome de usuário do perfil a ser investigado
        """
        if username and username.strip():
            self.queue.put(username.strip())
            logger.info(f"Perfil adicionado à fila: {username}")
    
    def add_profiles(self, usernames):
        """Adiciona múltiplos perfis à fila de processamento
        
        Args:
            usernames: Lista de nomes de usuário ou string com nomes separados por vírgula/linha
        """
        if isinstance(usernames, str):
            # Divide a string por vírgulas ou quebras de linha
            usernames = [u.strip() for u in usernames.replace('\n', ',').split(',')]
        
        for username in usernames:
            self.add_profile(username)
    
    def _worker(self):
        """Função de trabalho para processamento de perfis"""
        while not self.stop_event.is_set():
            try:
                # Tenta obter um perfil da fila (timeout para permitir verificação de parada)
                try:
                    username = self.queue.get(timeout=1)
                except:
                    continue
                
                # Processa o perfil
                try:
                    logger.info(f"Processando perfil: {username}")
                    result = self.data_extractor.investigate_profile(username)
                    
                    # Armazena o resultado
                    with self.lock:
                        self.results[username] = result
                    
                    success = True
                except Exception as e:
                    logger.error(f"Erro ao processar perfil {username}: {str(e)}")
                    with self.lock:
                        self.errors[username] = str(e)
                    
                    success = False
                
                # Notifica progresso
                if self.progress_callback:
                    with self.lock:
                        current = len(self.results) + len(self.errors)
                        total = current + self.queue.qsize()
                    
                    self.progress_callback(username, success, current, total)
                
                # Marca a tarefa como concluída
                self.queue.task_done()
                
                # Aguarda para evitar rate limiting
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Erro no worker: {str(e)}")
    
    def start(self):
        """Inicia o processamento em lote"""
        if self.workers:
            logger.warning("Processamento em lote já está em execução")
            return False
        
        # Reseta o estado
        self.results = {}
        self.errors = {}
        self.stop_event.clear()
        
        # Cria e inicia os workers
        self.workers = []
        for _ in range(self.max_concurrent):
            worker = threading.Thread(target=self._worker)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Processamento em lote iniciado com {self.max_concurrent} workers")
        
        # Inicia thread de monitoramento
        self.monitor_thread = threading.Thread(target=self._monitor)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        return True
    
    def _monitor(self):
        """Monitora a conclusão do processamento em lote"""
        self.queue.join()  # Aguarda até que todas as tarefas sejam concluídas
        
        # Notifica a conclusão
        if self.completion_callback:
            self.completion_callback(self.results, self.errors)
        
        # Limpa os workers
        self.stop()
    
    def stop(self):
        """Para o processamento em lote"""
        if not self.workers:
            return
        
        # Sinaliza para os workers pararem
        self.stop_event.set()
        
        # Aguarda os workers terminarem
        for worker in self.workers:
            if worker.is_alive():
                worker.join(1)  # Timeout de 1 segundo
        
        # Limpa a lista de workers
        self.workers = []
        
        logger.info("Processamento em lote interrompido")
    
    def get_results(self):
        """Retorna os resultados do processamento em lote"""
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_profiles": len(self.results) + len(self.errors),
            "successful": len(self.results),
            "failed": len(self.errors),
            "results": self.results,
            "errors": self.errors
        }
    
    def is_running(self):
        """Verifica se o processamento em lote está em execução"""
        return len(self.workers) > 0 and any(w.is_alive() for w in self.workers)
    
    def get_queue_size(self):
        """Retorna o número de perfis na fila"""
        return self.queue.qsize()