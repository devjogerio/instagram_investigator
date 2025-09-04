#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Deploy para Instagram Investigator
Automatiza configuração e deploy em diferentes ambientes
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path
import json

class DeployManager:
    """Gerenciador de deploy para Instagram Investigator"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.env_file = self.project_root / '.env'
        self.env_example = self.project_root / '.env.example'
    
    def check_requirements(self):
        """Verifica se todos os requisitos estão instalados"""
        print("Verificando requisitos...")
        
        # Verifica Python
        python_version = sys.version_info
        if python_version.major < 3 or python_version.minor < 8:
            print("❌ Python 3.8+ é necessário")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}")
        
        # Verifica pip
        try:
            subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                         check=True, capture_output=True)
            print("✅ pip disponível")
        except subprocess.CalledProcessError:
            print("❌ pip não encontrado")
            return False
        
        return True
    
    def setup_environment(self):
        """Configura ambiente virtual e dependências"""
        print("\nConfigurando ambiente...")
        
        # Cria ambiente virtual se não existir
        venv_path = self.project_root / '.venv'
        if not venv_path.exists():
            print("Criando ambiente virtual...")
            subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
        
        # Determina executável Python do venv
        if os.name == 'nt':  # Windows
            python_exe = venv_path / 'Scripts' / 'python.exe'
            pip_exe = venv_path / 'Scripts' / 'pip.exe'
        else:  # Linux/Mac
            python_exe = venv_path / 'bin' / 'python'
            pip_exe = venv_path / 'bin' / 'pip'
        
        # Atualiza pip
        print("Atualizando pip...")
        subprocess.run([str(pip_exe), 'install', '--upgrade', 'pip'], check=True)
        
        # Instala dependências
        print("Instalando dependências...")
        subprocess.run([str(pip_exe), 'install', '-r', 'requirements.txt'], check=True)
        
        if (self.project_root / 'requirements-test.txt').exists():
            subprocess.run([str(pip_exe), 'install', '-r', 'requirements-test.txt'], check=True)
        
        print("✅ Ambiente configurado")
        return str(python_exe)
    
    def setup_config(self):
        """Configura arquivos de configuração"""
        print("\nConfigurando arquivos...")
        
        # Cria .env se não existir
        if not self.env_file.exists() and self.env_example.exists():
            shutil.copy2(self.env_example, self.env_file)
            print(f"✅ Arquivo .env criado a partir de {self.env_example}")
            print("⚠️  Configure as variáveis de ambiente em .env antes de usar")
        
        # Cria diretórios necessários
        directories = ['logs', 'cache', 'exports/csv', 'exports/excel', 'exports/json', 'exports/pdf']
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print("✅ Diretórios criados")
    
    def run_tests(self, python_exe):
        """Executa testes da aplicação"""
        print("\nExecutando testes...")
        
        try:
            result = subprocess.run([
                python_exe, '-m', 'pytest', 'tests/', '-v'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                print("✅ Todos os testes passaram")
                return True
            else:
                print("❌ Alguns testes falharam:")
                print(result.stdout)
                print(result.stderr)
                return False
        
        except FileNotFoundError:
            print("⚠️  pytest não encontrado, pulando testes")
            return True
    
    def deploy_local(self):
        """Deploy para ambiente local"""
        print("\n=== Deploy Local ===")
        
        if not self.check_requirements():
            return False
        
        python_exe = self.setup_environment()
        self.setup_config()
        
        # Executa testes
        if not self.run_tests(python_exe):
            response = input("Testes falharam. Continuar mesmo assim? (y/N): ")
            if response.lower() != 'y':
                return False
        
        print("\n✅ Deploy local concluído!")
        print(f"Para executar: {python_exe} tkinter_app.py")
        return True
    
    def deploy_docker(self):
        """Deploy usando Docker"""
        print("\n=== Deploy Docker ===")
        
        # Verifica se Docker está disponível
        try:
            subprocess.run(['docker', '--version'], check=True, capture_output=True)
            print("✅ Docker disponível")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker não encontrado")
            return False
        
        # Verifica se docker-compose está disponível
        try:
            subprocess.run(['docker-compose', '--version'], check=True, capture_output=True)
            compose_cmd = 'docker-compose'
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(['docker', 'compose', 'version'], check=True, capture_output=True)
                compose_cmd = 'docker compose'
            except (subprocess.CalledProcessError, FileNotFoundError):
                print("❌ docker-compose não encontrado")
                return False
        
        print(f"✅ {compose_cmd} disponível")
        
        # Configura arquivos
        self.setup_config()
        
        # Build da imagem
        print("Construindo imagem Docker...")
        subprocess.run([compose_cmd.split()[0]] + compose_cmd.split()[1:] + ['build'], check=True)
        
        print("\n✅ Deploy Docker concluído!")
        print(f"Para executar: {compose_cmd} up")
        print(f"Para desenvolvimento: {compose_cmd} --profile dev up")
        return True
    
    def deploy_production(self):
        """Deploy para produção"""
        print("\n=== Deploy Produção ===")
        
        # Executa deploy local primeiro
        if not self.deploy_local():
            return False
        
        # Cria build executável
        print("\nCriando executável...")
        try:
            subprocess.run([sys.executable, 'build.py'], check=True)
            print("✅ Executável criado")
        except subprocess.CalledProcessError:
            print("❌ Falha ao criar executável")
            return False
        
        # Cria pacote de distribuição
        print("Criando pacote de distribuição...")
        dist_dir = self.project_root / 'distribution'
        dist_dir.mkdir(exist_ok=True)
        
        # Copia arquivos necessários
        files_to_copy = [
            'installer',
            'docs',
            'README.md',
            '.env.example'
        ]
        
        for item in files_to_copy:
            src = self.project_root / item
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, dist_dir / item, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dist_dir / item)
        
        print(f"✅ Pacote de distribuição criado em: {dist_dir}")
        return True
    
    def create_systemd_service(self):
        """Cria arquivo de serviço systemd para Linux"""
        service_content = f'''
[Unit]
Description=Instagram Investigator
After=network.target

[Service]
Type=simple
User=investigator
WorkingDirectory={self.project_root}
Environment=DISPLAY=:0
ExecStart={self.project_root}/.venv/bin/python tkinter_app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
'''
        
        service_file = self.project_root / 'instagram-investigator.service'
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"✅ Arquivo de serviço criado: {service_file}")
        print("Para instalar:")
        print(f"sudo cp {service_file} /etc/systemd/system/")
        print("sudo systemctl enable instagram-investigator")
        print("sudo systemctl start instagram-investigator")

def main():
    """Função principal"""
    parser = argparse.ArgumentParser(description='Deploy Instagram Investigator')
    parser.add_argument('environment', choices=['local', 'docker', 'production'],
                       help='Ambiente de deploy')
    parser.add_argument('--create-service', action='store_true',
                       help='Cria arquivo de serviço systemd')
    
    args = parser.parse_args()
    
    deploy_manager = DeployManager()
    
    print("🚀 Instagram Investigator - Deploy Manager")
    print(f"Ambiente: {args.environment}")
    
    success = False
    
    if args.environment == 'local':
        success = deploy_manager.deploy_local()
    elif args.environment == 'docker':
        success = deploy_manager.deploy_docker()
    elif args.environment == 'production':
        success = deploy_manager.deploy_production()
    
    if args.create_service:
        deploy_manager.create_systemd_service()
    
    if success:
        print("\n🎉 Deploy concluído com sucesso!")
    else:
        print("\n❌ Deploy falhou")
        sys.exit(1)

if __name__ == '__main__':
    main()