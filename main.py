#!/usr/bin/env python3
"""
Instagram Investigator - Aplicação Principal
Interface gráfica moderna com Tkinter para análise cross-platform de redes sociais
"""

import sys
import os
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'modules'))

# Importar a aplicação Tkinter
from tkinter_app import InstagramInvestigatorApp

def main():
    """
    Função principal da aplicação
    """
    try:
        # Verificar se o arquivo .env existe
        env_file = project_root / '.env'
        if not env_file.exists():
            print("Aviso: Arquivo .env não encontrado. Criando arquivo de exemplo...")
            
            # Criar arquivo .env.example se não existir
            env_example = project_root / '.env.example'
            if not env_example.exists():
                with open(env_example, 'w', encoding='utf-8') as f:
                    f.write("""# Configurações do Instagram Investigator

# Instagram API
INSTAGRAM_USERNAME=seu_usuario_instagram
INSTAGRAM_PASSWORD=sua_senha_instagram

# Facebook API
FACEBOOK_APP_ID=seu_app_id_facebook
FACEBOOK_APP_SECRET=seu_app_secret_facebook
FACEBOOK_ACCESS_TOKEN=seu_access_token_facebook

# Twitter API (Opcional)
TWITTER_API_KEY=sua_api_key_twitter
TWITTER_API_SECRET=sua_api_secret_twitter
TWITTER_ACCESS_TOKEN=seu_access_token_twitter
TWITTER_ACCESS_TOKEN_SECRET=seu_access_token_secret_twitter

# LinkedIn API (Opcional)
LINKEDIN_CLIENT_ID=seu_client_id_linkedin
LINKEDIN_CLIENT_SECRET=seu_client_secret_linkedin

# TikTok API (Opcional)
TIKTOK_CLIENT_KEY=sua_client_key_tiktok
TIKTOK_CLIENT_SECRET=seu_client_secret_tiktok

# Configurações de Cache
CACHE_ENABLED=true
CACHE_DURATION_HOURS=24

# Configurações de Exportação
EXPORT_DIRECTORY=exports
MAX_EXPORT_FILES=50
""")
            
            print(f"Arquivo .env.example criado em: {env_example}")
            print("Configure suas credenciais copiando .env.example para .env")
        
        # Criar diretórios necessários
        directories = [
            project_root / 'exports',
            project_root / 'cache',
            project_root / 'logs',
            project_root / 'temp'
        ]
        
        for directory in directories:
            directory.mkdir(exist_ok=True)
        
        # Inicializar e executar a aplicação
        print("Iniciando Instagram Investigator...")
        app = InstagramInvestigatorApp()
        app.run()
        
    except KeyboardInterrupt:
        print("\nAplicação interrompida pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"Erro fatal ao inicializar aplicação: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()