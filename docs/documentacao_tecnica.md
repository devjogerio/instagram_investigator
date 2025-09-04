# Documentação Técnica - Instagram Investigator

## Visão Geral

O Instagram Investigator é uma ferramenta de análise cross-platform que permite investigar perfis de usuários em múltiplas redes sociais, realizando análises comparativas e gerando relatórios detalhados.

## Arquitetura do Sistema

### Estrutura de Diretórios

```
instagram_investigator/
├── main.py                 # Ponto de entrada da aplicação
├── tkinter_app.py         # Interface gráfica principal
├── requirements.txt       # Dependências do projeto
├── .env.example          # Exemplo de variáveis de ambiente
├── modules/              # Módulos principais
│   ├── instagram_api.py  # API do Instagram
│   ├── facebook_api.py   # API do Facebook
│   ├── twitter_api.py    # API do Twitter/X
│   ├── linkedin_api.py   # API do LinkedIn
│   ├── tiktok_api.py     # API do TikTok
│   ├── cross_platform_analyzer.py    # Análise cross-platform
│   ├── export_manager.py             # Gerenciamento de exportações
│   ├── cache_manager.py              # Sistema de cache
│   ├── tkinter_ui_components.py      # Componentes UI reutilizáveis
│   └── tkinter_visualizations.py     # Sistema de visualizações
├── cache/               # Cache de dados
├── exports/            # Arquivos exportados
├── logs/              # Logs da aplicação
├── tests/             # Testes automatizados
└── docs/              # Documentação
```

### Componentes Principais

#### 1. Interface Gráfica (Tkinter)
- **Arquivo**: `tkinter_app.py`
- **Responsabilidade**: Interface principal da aplicação
- **Funcionalidades**:
  - Abas de pesquisa, resultados, visualizações, exportação e configurações
  - Tema personalizado com cores consistentes
  - Integração com todos os módulos do sistema

#### 2. APIs das Plataformas
- **Instagram API** (`instagram_api.py`): Extração de dados do Instagram
- **Facebook API** (`facebook_api.py`): Integração com Facebook Graph API
- **Twitter API** (`twitter_api.py`): Acesso aos dados do Twitter/X
- **LinkedIn API** (`linkedin_api.py`): Extração de perfis profissionais
- **TikTok API** (`tiktok_api.py`): Dados de perfis do TikTok

#### 3. Análise Cross-Platform
- **Arquivo**: `cross_platform_analyzer.py`
- **Funcionalidades**:
  - Correspondência de identidade entre plataformas
  - Análise de sobreposição de audiência
  - Detecção de padrões comportamentais
  - Métricas de engajamento comparativas

#### 4. Sistema de Visualizações
- **Arquivo**: `tkinter_visualizations.py`
- **Tecnologias**: matplotlib, seaborn
- **Tipos de Gráficos**:
  - Comparação de engajamento
  - Métricas de crescimento
  - Distribuição de conteúdo
  - Dashboard abrangente

#### 5. Gerenciamento de Exportações
- **Arquivo**: `export_manager.py`
- **Formatos Suportados**:
  - JSON: Dados estruturados
  - CSV: Planilhas simples
  - PDF: Relatórios visuais
  - Excel: Planilhas avançadas

#### 6. Sistema de Cache
- **Arquivo**: `cache_manager.py`
- **Funcionalidades**:
  - Cache de requisições API
  - Otimização de performance
  - Gerenciamento de TTL (Time To Live)

## Configuração do Ambiente

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example`:

```env
# Instagram
INSTAGRAM_USERNAME=seu_usuario
INSTAGRAM_PASSWORD=sua_senha

# Facebook
FACEBOOK_APP_ID=seu_app_id
FACEBOOK_APP_SECRET=seu_app_secret
FACEBOOK_ACCESS_TOKEN=seu_token

# Twitter/X
TWITTER_API_KEY=sua_api_key
TWITTER_API_SECRET=seu_api_secret
TWITTER_ACCESS_TOKEN=seu_access_token
TWITTER_ACCESS_TOKEN_SECRET=seu_token_secret

# LinkedIn
LINKEDIN_CLIENT_ID=seu_client_id
LINKEDIN_CLIENT_SECRET=seu_client_secret

# TikTok
TIKTOK_ACCESS_TOKEN=seu_access_token
```

### Instalação

1. Clone o repositório
2. Crie um ambiente virtual: `python -m venv .venv`
3. Ative o ambiente: `.venv\Scripts\activate` (Windows) ou `source .venv/bin/activate` (Linux/Mac)
4. Instale dependências: `pip install -r requirements.txt`
5. Configure o arquivo `.env`
6. Execute: `python main.py`

## Fluxo de Dados

1. **Entrada**: Usuário insere nome de usuário e seleciona plataformas
2. **Coleta**: APIs coletam dados de cada plataforma selecionada
3. **Cache**: Dados são armazenados em cache para otimização
4. **Análise**: Sistema realiza análise cross-platform
5. **Visualização**: Gráficos são gerados com matplotlib
6. **Exportação**: Dados podem ser exportados em múltiplos formatos

## Segurança

- **Credenciais**: Todas as credenciais ficam no arquivo `.env`
- **Cache**: Dados sensíveis não são persistidos permanentemente
- **Logs**: Informações sensíveis não são registradas em logs
- **APIs**: Rate limiting implementado para evitar bloqueios

## Performance

- **Threading**: Pesquisas executadas em threads separadas
- **Cache**: Sistema de cache reduz requisições desnecessárias
- **Lazy Loading**: Visualizações carregadas sob demanda
- **Otimização**: Componentes UI otimizados para responsividade

## Extensibilidade

### Adicionando Nova Plataforma

1. Crie arquivo `nova_plataforma_api.py` em `modules/`
2. Implemente classe seguindo padrão das APIs existentes
3. Adicione importação condicional em `tkinter_app.py`
4. Inclua checkbox na interface de seleção
5. Atualize documentação

### Adicionando Novo Formato de Exportação

1. Modifique `export_manager.py`
2. Implemente método de exportação específico
3. Adicione checkbox na interface de exportação
4. Teste integração completa

## Testes

Execute os testes com:
```bash
python -m pytest tests/
```

Tipos de teste:
- **Unitários**: Testam módulos individuais
- **Integração**: Testam interação entre componentes
- **API**: Testam conectividade com APIs externas

## Troubleshooting

### Problemas Comuns

1. **Erro de Autenticação**: Verifique credenciais no `.env`
2. **Rate Limiting**: Aguarde antes de fazer novas requisições
3. **Dependências**: Execute `pip install -r requirements.txt`
4. **Interface não carrega**: Verifique se Tkinter está instalado

### Logs

Logs são salvos em `logs/` com timestamp. Níveis:
- **INFO**: Operações normais
- **WARNING**: Situações de atenção
- **ERROR**: Erros que impedem operação
- **DEBUG**: Informações detalhadas para desenvolvimento

## Manutenção

### Atualizações Regulares

1. **Dependências**: Mantenha bibliotecas atualizadas
2. **APIs**: Monitore mudanças nas APIs das plataformas
3. **Cache**: Limpe cache periodicamente
4. **Logs**: Rotacione logs antigos

### Monitoramento

- Taxa de sucesso das requisições API
- Tempo de resposta das operações
- Uso de memória e CPU
- Tamanho do cache

---

*Documentação atualizada em: Janeiro 2025*
*Versão: 2.0 (Tkinter)*