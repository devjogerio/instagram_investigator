# Guia de Deploy - Instagram Investigator

Este guia fornece instruções completas para deploy do Instagram Investigator em diferentes ambientes.

## 📋 Pré-requisitos

### Requisitos Mínimos
- Python 3.8 ou superior
- 4GB RAM
- 2GB espaço em disco
- Sistema operacional: Windows 10+, Linux (Ubuntu 18.04+), macOS 10.14+

### Dependências do Sistema

#### Windows
```bash
# Nenhuma dependência adicional necessária
# Python já inclui tkinter
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install python3-tk python3-dev build-essential
```

#### macOS
```bash
# Instalar via Homebrew
brew install python-tk
```

## 🚀 Métodos de Deploy

### 1. Deploy Local (Desenvolvimento)

#### Instalação Automática
```bash
python deploy.py local
```

#### Instalação Manual
```bash
# 1. Criar ambiente virtual
python -m venv .venv

# 2. Ativar ambiente virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar ambiente
cp .env.example .env
# Editar .env com suas configurações

# 5. Executar aplicação
python tkinter_app.py
```

### 2. Deploy com Docker

#### Pré-requisitos
- Docker 20.10+
- Docker Compose 2.0+

#### Instalação
```bash
# Deploy automático
python deploy.py docker

# Ou manualmente:
docker-compose up --build
```

#### Configuração para GUI (Linux)
```bash
# Permitir conexões X11
xhost +local:docker

# Executar com display
DISPLAY=$DISPLAY docker-compose up
```

#### Modo Desenvolvimento
```bash
docker-compose --profile dev up
```

### 3. Deploy de Produção

#### Executável Standalone
```bash
# Gerar executável
python deploy.py production

# Ou manualmente:
python build.py
```

#### Instalação do Executável
1. Navegue até a pasta `installer/`
2. Execute `install.bat` como administrador (Windows)
3. O aplicativo será instalado em `C:\Program Files\InstagramInvestigator`

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
# Configurações da API do Instagram
INSTAGRAM_USERNAME=seu_usuario
INSTAGRAM_PASSWORD=sua_senha

# Configurações de outras redes sociais (opcional)
TWITTER_API_KEY=sua_chave
TWITTER_API_SECRET=seu_segredo
FACEBOOK_ACCESS_TOKEN=seu_token
LINKEDIN_CLIENT_ID=seu_client_id

# Configurações de logging
LOG_LEVEL=INFO
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# Configurações de cache
CACHE_ENABLED=true
CACHE_TTL=3600

# Configurações de monitoramento
MONITORING_ENABLED=true
MONITORING_INTERVAL=60
```

### Configuração de Proxy (Opcional)

```env
# Configurações de proxy
HTTP_PROXY=http://proxy.exemplo.com:8080
HTTPS_PROXY=https://proxy.exemplo.com:8080
NO_PROXY=localhost,127.0.0.1
```

## 🐧 Deploy em Servidor Linux

### Como Serviço Systemd

```bash
# 1. Criar usuário para o serviço
sudo useradd -m -s /bin/bash investigator

# 2. Copiar aplicação
sudo cp -r /caminho/para/instagram_investigator /opt/
sudo chown -R investigator:investigator /opt/instagram_investigator

# 3. Criar arquivo de serviço
python deploy.py local --create-service
sudo cp instagram-investigator.service /etc/systemd/system/

# 4. Habilitar e iniciar serviço
sudo systemctl daemon-reload
sudo systemctl enable instagram-investigator
sudo systemctl start instagram-investigator

# 5. Verificar status
sudo systemctl status instagram-investigator
```

### Configuração X11 para GUI Remota

```bash
# 1. Instalar X11 forwarding
sudo apt-get install xauth

# 2. Configurar SSH
# Em /etc/ssh/sshd_config:
X11Forwarding yes
X11DisplayOffset 10
X11UseLocalhost no

# 3. Conectar com X11 forwarding
ssh -X usuario@servidor

# 4. Executar aplicação
DISPLAY=:10.0 python tkinter_app.py
```

## 🪟 Deploy no Windows Server

### Como Serviço Windows

```powershell
# 1. Instalar NSSM (Non-Sucking Service Manager)
# Baixar de: https://nssm.cc/download

# 2. Criar serviço
nssm install "Instagram Investigator" "C:\caminho\para\.venv\Scripts\python.exe" "C:\caminho\para\tkinter_app.py"

# 3. Configurar serviço
nssm set "Instagram Investigator" AppDirectory "C:\caminho\para\instagram_investigator"
nssm set "Instagram Investigator" DisplayName "Instagram Investigator"
nssm set "Instagram Investigator" Description "Ferramenta OSINT para análise do Instagram"

# 4. Iniciar serviço
net start "Instagram Investigator"
```

## 🔍 Monitoramento e Logs

### Localização dos Logs
- **Aplicação**: `logs/app.log`
- **Erros**: `logs/errors.log`
- **API**: `logs/api_calls.log`
- **Sistema**: `logs/instagram_investigator_YYYYMMDD_HHMMSS.log`

### Monitoramento de Saúde

```bash
# Verificar saúde da aplicação
curl -f http://localhost:8080/health || echo "Aplicação não está respondendo"

# Verificar logs em tempo real
tail -f logs/app.log

# Verificar uso de recursos
ps aux | grep python
df -h
free -m
```

## 🛠️ Solução de Problemas

### Problemas Comuns

#### Erro: "No module named 'tkinter'"
```bash
# Linux
sudo apt-get install python3-tk

# macOS
brew install python-tk
```

#### Erro: "Permission denied" ao criar logs
```bash
# Verificar permissões
ls -la logs/

# Corrigir permissões
chmod 755 logs/
chown -R $USER:$USER logs/
```

#### Aplicação não inicia no Docker
```bash
# Verificar logs do container
docker-compose logs instagram-investigator

# Verificar se X11 está configurado (Linux)
echo $DISPLAY
xhost +local:docker
```

#### Alto uso de memória
```bash
# Verificar configurações de cache
grep CACHE .env

# Reduzir TTL do cache
echo "CACHE_TTL=1800" >> .env
```

### Logs de Debug

```bash
# Habilitar debug
echo "LOG_LEVEL=DEBUG" >> .env

# Executar com debug
python -u tkinter_app.py 2>&1 | tee debug.log
```

## 📊 Métricas e Performance

### Monitoramento de Performance

```python
# Verificar métricas do sistema
from modules.system_monitor import get_system_monitor

monitor = get_system_monitor()
health_report = monitor.generate_health_report()
print(health_report)
```

### Otimização

1. **Cache**: Habilite cache para melhor performance
2. **Logs**: Configure rotação de logs para evitar crescimento excessivo
3. **Recursos**: Monitore uso de CPU e memória
4. **Rede**: Configure timeouts apropriados para APIs

## 🔐 Segurança

### Boas Práticas

1. **Credenciais**: Nunca commite credenciais no código
2. **Permissões**: Execute com usuário não-privilegiado
3. **Firewall**: Configure firewall para portas necessárias
4. **Updates**: Mantenha dependências atualizadas
5. **Logs**: Não registre informações sensíveis

### Auditoria

```bash
# Verificar dependências vulneráveis
pip audit

# Verificar permissões de arquivos
find . -type f -perm /o+w

# Verificar logs de segurança
grep -i "error\|warning\|failed" logs/app.log
```

## 📞 Suporte

Para suporte técnico:

1. Verifique os logs em `logs/`
2. Execute diagnósticos: `python -m modules.system_monitor`
3. Consulte a documentação técnica em `docs/`
4. Reporte issues com logs e configuração

---

**Nota**: Este guia assume conhecimento básico de administração de sistemas. Para ambientes de produção críticos, consulte um especialista em DevOps.