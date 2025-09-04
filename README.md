# Instagram Investigator 🔍

> Ferramenta avançada de análise cross-platform para investigação de perfis em redes sociais

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Sobre o Projeto

O Instagram Investigator é uma aplicação desktop desenvolvida em Python com interface Tkinter que permite:

- 🔍 **Pesquisa Cross-Platform**: Investigue perfis em múltiplas redes sociais simultaneamente
- 📊 **Análises Avançadas**: Compare métricas de engajamento entre plataformas
- 📈 **Visualizações Interativas**: Gráficos detalhados com matplotlib e seaborn
- 📄 **Exportação Múltipla**: Relatórios em JSON, CSV, PDF e Excel
- ⚡ **Cache Inteligente**: Sistema otimizado para melhor performance
- 🎨 **Interface Moderna**: Design limpo e intuitivo com Tkinter

## 🚀 Funcionalidades

### Plataformas Suportadas
- ✅ Instagram
- ✅ Facebook
- ✅ Twitter/X
- ✅ LinkedIn
- ✅ TikTok

### Tipos de Análise
- **Análise de Perfil**: Dados básicos, seguidores, seguindo
- **Métricas de Engajamento**: Likes, comentários, compartilhamentos
- **Análise Temporal**: Crescimento ao longo do tempo
- **Comparação Cross-Platform**: Correlações entre plataformas
- **Detecção de Padrões**: Comportamentos e tendências

### Formatos de Exportação
- **JSON**: Dados estruturados para integração
- **CSV**: Planilhas para análise externa
- **PDF**: Relatórios visuais profissionais
- **Excel**: Planilhas avançadas com múltiplas abas

## Aviso Legal

**ATENÇÃO:** Esta ferramenta deve ser utilizada apenas para fins educacionais, de pesquisa e marketing legítimo. O uso desta ferramenta pode violar os Termos de Serviço do Instagram. O usuário é o único responsável pelo uso adequado e legal desta aplicação.

## 🛠️ Instalação

### Pré-requisitos
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git (opcional)

### Passo a Passo

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/instagram-investigator.git
   cd instagram-investigator
   ```

2. **Crie um ambiente virtual**
   ```bash
   python -m venv .venv
   ```

3. **Ative o ambiente virtual**
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source .venv/bin/activate
     ```

4. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

5. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite o arquivo .env com suas credenciais
   ```

6. **Execute a aplicação**
   ```bash
   python main.py
   ```

## ⚙️ Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` baseado no `.env.example` e configure suas credenciais:

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

## 📖 Como Usar

### Interface Principal

1. **Aba Pesquisa** 🔍
   - Digite o nome de usuário a ser investigado
   - Selecione as plataformas desejadas
   - Clique em "Iniciar Pesquisa"

2. **Aba Resultados** 📊
   - Visualize os dados coletados de cada plataforma
   - Compare métricas básicas
   - Acesse análise cross-platform

3. **Aba Visualizações** 📈
   - Gráficos de engajamento
   - Métricas de crescimento
   - Distribuição de conteúdo
   - Dashboard completo

4. **Aba Exportação** 📄
   - Selecione formatos de exportação
   - Gere relatórios personalizados
   - Visualize histórico de exportações

5. **Aba Configurações** ⚙️
   - Configure APIs disponíveis
   - Ajuste preferências do sistema
   - Gerencie cache e logs

## 🧪 Testes

Execute os testes automatizados:

```bash
# Todos os testes
python -m pytest tests/

# Testes específicos
python -m pytest tests/test_instagram_api.py

# Com cobertura
python -m pytest tests/ --cov=modules
```

## 📁 Estrutura do Projeto

```
instagram_investigator/
├── 📄 main.py                    # Ponto de entrada
├── 🖥️ tkinter_app.py             # Interface principal
├── 📋 requirements.txt           # Dependências
├── 🔧 .env.example              # Exemplo de configuração
├── 📂 modules/                  # Módulos principais
│   ├── 📱 instagram_api.py      # API Instagram
│   ├── 📘 facebook_api.py       # API Facebook
│   ├── 🐦 twitter_api.py        # API Twitter
│   ├── 💼 linkedin_api.py       # API LinkedIn
│   ├── 🎵 tiktok_api.py         # API TikTok
│   ├── 🔄 cross_platform_analyzer.py
│   ├── 📊 export_manager.py
│   ├── 💾 cache_manager.py
│   ├── 🎨 tkinter_ui_components.py
│   └── 📈 tkinter_visualizations.py
├── 📂 cache/                   # Cache de dados
├── 📂 exports/                 # Arquivos exportados
├── 📂 logs/                    # Logs da aplicação
├── 📂 tests/                   # Testes automatizados
└── 📂 docs/                    # Documentação
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Diretrizes de Contribuição

- Siga o padrão de código existente
- Adicione testes para novas funcionalidades
- Atualize a documentação quando necessário
- Use commits semânticos

## 🐛 Problemas Conhecidos

- **Rate Limiting**: APIs podem limitar requisições frequentes
- **Autenticação**: Credenciais podem expirar periodicamente
- **Dependências**: Algumas bibliotecas podem ter conflitos

## 🔄 Roadmap

- [ ] Suporte a mais plataformas (YouTube, Pinterest)
- [ ] Interface web complementar
- [ ] API REST para integração
- [ ] Machine Learning para detecção de padrões
- [ ] Relatórios automatizados por email
- [ ] Dashboard em tempo real

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Seu Nome** - *Desenvolvimento inicial* - [SeuGitHub](https://github.com/seu-usuario)

## 🙏 Agradecimentos

- Comunidade Python pela excelente documentação
- Desenvolvedores das APIs das redes sociais
- Contribuidores do projeto
- Bibliotecas open source utilizadas

## 📞 Suporte

Se você encontrar algum problema ou tiver dúvidas:

1. Verifique a [documentação técnica](docs/documentacao_tecnica.md)
2. Procure em [Issues existentes](https://github.com/seu-usuario/instagram-investigator/issues)
3. Crie uma nova [Issue](https://github.com/seu-usuario/instagram-investigator/issues/new)
4. Entre em contato: seu-email@exemplo.com

---

⭐ **Se este projeto foi útil para você, considere dar uma estrela!** ⭐