# Guia de Instalação e Configuração

## Pré-requisitos do Sistema

### Requisitos Mínimos
- **Sistema Operacional**: Windows 10/11, macOS 10.14+, ou Linux Ubuntu 18.04+
- **Python**: Versão 3.8 ou superior
- **RAM**: Mínimo 4GB (recomendado 8GB)
- **Espaço em Disco**: 500MB livres
- **Conexão**: Internet estável

### Verificando o Python

Antes de começar, verifique se o Python está instalado:

```bash
python --version
# ou
python3 --version
```

Se não estiver instalado, baixe em: https://python.org/downloads/

## Instalação Passo a Passo

### 1. Download do Projeto

#### Opção A: Via Git (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/instagram-investigator.git

# Entre no diretório
cd instagram-investigator
```

#### Opção B: Download Direto

1. Acesse o repositório no GitHub
2. Clique em "Code" → "Download ZIP"
3. Extraia o arquivo ZIP
4. Abra o terminal na pasta extraída

### 2. Configuração do Ambiente Virtual

#### Windows

```cmd
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual
.venv\Scripts\activate

# Verificar ativação (deve mostrar (.venv) no prompt)
```

#### macOS/Linux

```bash
# Criar ambiente virtual
python3 -m venv .venv

# Ativar ambiente virtual
source .venv/bin/activate

# Verificar ativação (deve mostrar (.venv) no prompt)
```

### 3. Instalação das Dependências

```bash
# Atualizar pip
python -m pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt
```

**Se houver erros de instalação:**

```bash
# Para Windows (se houver problemas com compilação)
pip install --only-binary=all -r requirements.txt

# Para macOS (se houver problemas com Tkinter)
brew install python-tk

# Para Linux (Ubuntu/Debian)
sudo apt-get install python3-tk
```

### 4. Configuração das Variáveis de Ambiente

#### Criar arquivo .env

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar arquivo (use seu editor preferido)
nano .env
# ou
code .env
# ou
notepad .env
```

#### Configurar credenciais no .env

```env
# Instagram (obrigatório para funcionalidade básica)
INSTAGRAM_USERNAME=seu_usuario_instagram
INSTAGRAM_PASSWORD=sua_senha_instagram

# Facebook (opcional)
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
FACEBOOK_ACCESS_TOKEN=

# Twitter/X (opcional)
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=

# LinkedIn (opcional)
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=

# TikTok (opcional)
TIKTOK_ACCESS_TOKEN=
```

### 5. Teste da Instalação

```bash
# Executar aplicação
python main.py
```

Se tudo estiver correto, a interface gráfica deve abrir.

## Configuração das APIs

### Instagram (Essencial)

**Método 1: Credenciais Pessoais (Mais Simples)**

1. Use suas credenciais normais do Instagram
2. **IMPORTANTE**: Use uma conta secundária se possível
3. Configure no arquivo `.env`:

```env
INSTAGRAM_USERNAME=sua_conta_instagram
INSTAGRAM_PASSWORD=sua_senha
```

**Método 2: Session ID (Alternativo)**

1. Faça login no Instagram pelo navegador
2. Abra as ferramentas de desenvolvedor (F12)
3. Vá para "Application" → "Cookies" → "https://www.instagram.com"
4. Copie o valor do cookie "sessionid"
5. Configure no código (não recomendado para produção)

### Facebook (Opcional)

1. Acesse [Facebook Developers](https://developers.facebook.com/)
2. Crie uma nova aplicação:
   - Clique em "Create App"
   - Escolha "Consumer" ou "Business"
   - Preencha nome e email
3. No painel da aplicação:
   - Vá em "Settings" → "Basic"
   - Copie "App ID" e "App Secret"
4. Gere um Access Token:
   - Vá em "Tools" → "Graph API Explorer"
   - Selecione sua aplicação
   - Gere um token com permissões necessárias

```env
FACEBOOK_APP_ID=seu_app_id
FACEBOOK_APP_SECRET=seu_app_secret
FACEBOOK_ACCESS_TOKEN=seu_access_token
```

### Twitter/X (Opcional)

1. Acesse [Twitter Developer Portal](https://developer.twitter.com/)
2. Candidate-se para uma conta de desenvolvedor
3. Crie um novo projeto e aplicação
4. Gere as chaves necessárias:
   - API Key e API Secret
   - Access Token e Access Token Secret

```env
TWITTER_API_KEY=sua_api_key
TWITTER_API_SECRET=sua_api_secret
TWITTER_ACCESS_TOKEN=seu_access_token
TWITTER_ACCESS_TOKEN_SECRET=seu_access_token_secret
```

### LinkedIn (Opcional)

1. Acesse [LinkedIn Developers](https://www.linkedin.com/developers/)
2. Crie uma nova aplicação
3. Configure as permissões necessárias
4. Obtenha Client ID e Client Secret

```env
LINKEDIN_CLIENT_ID=seu_client_id
LINKEDIN_CLIENT_SECRET=seu_client_secret
```

### TikTok (Opcional)

1. Acesse [TikTok Developers](https://developers.tiktok.com/)
2. Registre sua aplicação
3. Obtenha o Access Token

```env
TIKTOK_ACCESS_TOKEN=seu_access_token
```

## Solução de Problemas Comuns

### Erro: "ModuleNotFoundError"

```bash
# Verificar se o ambiente virtual está ativo
# Deve mostrar (.venv) no prompt

# Se não estiver ativo:
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Reinstalar dependências
pip install -r requirements.txt
```

### Erro: "Tkinter not found"

**Windows:**
- Reinstale o Python marcando "tcl/tk and IDLE"
- Ou baixe Python do site oficial

**macOS:**
```bash
brew install python-tk
# ou
brew install tcl-tk
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3-tk
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install tkinter
# ou
sudo dnf install python3-tkinter
```

### Erro: "Permission denied" ou "Access denied"

**Windows:**
```cmd
# Executar como administrador ou verificar antivírus
# Adicionar pasta do projeto às exceções do antivírus
```

**macOS/Linux:**
```bash
# Verificar permissões da pasta
ls -la

# Corrigir permissões se necessário
chmod -R 755 .
```

### Erro: "Instagram login failed"

1. **Verificar credenciais**: Confirme usuário e senha
2. **Autenticação de dois fatores**: Desative temporariamente
3. **Captcha**: Instagram pode solicitar verificação
4. **Rate limiting**: Aguarde alguns minutos entre tentativas
5. **Conta bloqueada**: Use conta diferente

### Erro: "API rate limit exceeded"

```python
# Aguardar antes de nova tentativa
# O sistema tem rate limiting automático
# Aguarde 15-30 minutos entre pesquisas intensivas
```

### Interface não abre ou trava

1. **Verificar display** (Linux):
```bash
export DISPLAY=:0
python main.py
```

2. **Verificar resolução de tela**:
   - Interface otimizada para 1024x768 ou superior

3. **Verificar recursos do sistema**:
   - Feche outros programas pesados
   - Verifique uso de RAM

## Configurações Avançadas

### Configuração de Proxy

Se você usa proxy corporativo:

```env
# Adicionar ao .env
HTTP_PROXY=http://proxy.empresa.com:8080
HTTPS_PROXY=https://proxy.empresa.com:8080
```

### Configuração de Cache

```env
# Configurações de cache (opcional)
CACHE_TTL=3600  # 1 hora em segundos
CACHE_MAX_SIZE=100  # Máximo de entradas
```

### Configuração de Logs

```env
# Nível de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Atualização do Sistema

### Atualizar para nova versão

```bash
# Fazer backup das configurações
cp .env .env.backup

# Atualizar código
git pull origin main
# ou baixar nova versão e substituir arquivos

# Atualizar dependências
pip install -r requirements.txt --upgrade

# Restaurar configurações
cp .env.backup .env
```

### Verificar versão atual

```bash
# No terminal da aplicação ou logs
python main.py --version
```

## Desinstalação

### Remover completamente

```bash
# Desativar ambiente virtual
deactivate

# Remover pasta do projeto
rm -rf instagram-investigator  # Linux/macOS
# ou deletar pasta manualmente no Windows

# Remover dados de cache (opcional)
rm -rf ~/.instagram_investigator_cache
```

## Configuração para Desenvolvimento

### Ambiente de desenvolvimento

```bash
# Instalar dependências de desenvolvimento
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
pre-commit install

# Executar testes
python -m pytest tests/

# Executar com debug
python main.py --debug
```

### Estrutura de desenvolvimento

```
instagram_investigator/
├── .venv/                  # Ambiente virtual
├── modules/               # Código fonte
├── tests/                 # Testes automatizados
├── docs/                  # Documentação
├── logs/                  # Logs da aplicação
├── cache/                 # Cache de dados
├── exports/               # Arquivos exportados
├── .env                   # Configurações (não versionar)
├── .env.example          # Exemplo de configurações
├── requirements.txt       # Dependências de produção
├── requirements-dev.txt   # Dependências de desenvolvimento
└── README.md             # Documentação principal
```

## Suporte e Ajuda

### Recursos de ajuda

1. **Documentação**: Consulte `docs/` para documentação completa
2. **Issues**: Reporte problemas no GitHub
3. **Logs**: Verifique `logs/app.log` para detalhes de erros
4. **Comunidade**: Participe das discussões no GitHub

### Informações para suporte

Ao reportar problemas, inclua:

```bash
# Versão do Python
python --version

# Sistema operacional
# Windows: winver
# macOS: sw_vers
# Linux: lsb_release -a

# Logs relevantes
tail -n 50 logs/app.log

# Dependências instaladas
pip list
```

---

**Instalação concluída com sucesso!** 🎉

Agora você pode executar `python main.py` e começar a usar o Instagram Investigator.

Para dúvidas ou problemas, consulte a [documentação técnica](documentacao_tecnica.md) ou abra uma issue no GitHub.