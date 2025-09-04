# Referência da API - Instagram Investigator

## Visão Geral

Esta documentação descreve as APIs internas do Instagram Investigator, permitindo que desenvolvedores entendam e estendam o sistema.

## Módulos Principais

### 1. Instagram API (`instagram_api.py`)

#### Classe: `InstagramAPI`

```python
class InstagramAPI:
    def __init__(self, username: str = None, password: str = None)
    def get_user_info(self, username: str) -> dict
    def get_user_posts(self, username: str, limit: int = 20) -> list
    def get_user_followers(self, username: str, limit: int = 100) -> list
    def get_user_following(self, username: str, limit: int = 100) -> list
    def is_available(self) -> bool
```

**Métodos:**

- `get_user_info(username)`: Retorna informações básicas do perfil
- `get_user_posts(username, limit)`: Obtém posts recentes do usuário
- `get_user_followers(username, limit)`: Lista de seguidores
- `get_user_following(username, limit)`: Lista de pessoas seguidas
- `is_available()`: Verifica se a API está configurada

**Exemplo de Uso:**

```python
from modules.instagram_api import InstagramAPI

api = InstagramAPI(username="seu_usuario", password="sua_senha")
user_info = api.get_user_info("target_username")
print(f"Seguidores: {user_info['followers_count']}")
```

**Retorno de `get_user_info()`:**

```json
{
    "username": "exemplo_usuario",
    "full_name": "Nome Completo",
    "biography": "Biografia do usuário",
    "followers_count": 1500,
    "following_count": 300,
    "posts_count": 120,
    "is_private": false,
    "is_verified": false,
    "profile_pic_url": "https://...",
    "external_url": "https://..."
}
```

### 2. Facebook API (`facebook_api.py`)

#### Classe: `FacebookAPI`

```python
class FacebookAPI:
    def __init__(self, app_id: str = None, app_secret: str = None, access_token: str = None)
    def get_user_info(self, user_id: str) -> dict
    def get_page_info(self, page_id: str) -> dict
    def get_page_posts(self, page_id: str, limit: int = 20) -> list
    def is_available(self) -> bool
```

**Exemplo de Uso:**

```python
from modules.facebook_api import FacebookAPI

api = FacebookAPI(
    app_id="seu_app_id",
    app_secret="seu_app_secret",
    access_token="seu_token"
)
page_info = api.get_page_info("page_id")
```

### 3. Twitter API (`twitter_api.py`)

#### Classe: `TwitterAPI`

```python
class TwitterAPI:
    def __init__(self, api_key: str = None, api_secret: str = None, 
                 access_token: str = None, access_token_secret: str = None)
    def get_user_info(self, username: str) -> dict
    def get_user_tweets(self, username: str, limit: int = 20) -> list
    def get_user_followers(self, username: str, limit: int = 100) -> list
    def is_available(self) -> bool
```

### 4. Cross-Platform Analyzer (`cross_platform_analyzer.py`)

#### Classe: `CrossPlatformAnalyzer`

```python
class CrossPlatformAnalyzer:
    def __init__(self)
    def analyze_user(self, username: str, platforms: list) -> dict
    def compare_engagement(self, data: dict) -> dict
    def find_correlations(self, data: dict) -> dict
    def generate_insights(self, data: dict) -> list
```

**Métodos Principais:**

- `analyze_user(username, platforms)`: Análise completa cross-platform
- `compare_engagement(data)`: Comparação de métricas de engajamento
- `find_correlations(data)`: Identifica correlações entre plataformas
- `generate_insights(data)`: Gera insights automáticos

**Exemplo de Uso:**

```python
from modules.cross_platform_analyzer import CrossPlatformAnalyzer

analyzer = CrossPlatformAnalyzer()
results = analyzer.analyze_user(
    username="target_user",
    platforms=["instagram", "twitter", "facebook"]
)

engagement = analyzer.compare_engagement(results)
insights = analyzer.generate_insights(results)
```

**Estrutura de Retorno:**

```json
{
    "username": "target_user",
    "platforms": {
        "instagram": {
            "available": true,
            "data": {...},
            "metrics": {...}
        },
        "twitter": {
            "available": true,
            "data": {...},
            "metrics": {...}
        }
    },
    "cross_analysis": {
        "engagement_comparison": {...},
        "audience_overlap": {...},
        "content_patterns": {...}
    },
    "insights": [
        "Maior engajamento no Instagram",
        "Crescimento consistente no Twitter"
    ]
}
```

### 5. Export Manager (`export_manager.py`)

#### Classe: `ExportManager`

```python
class ExportManager:
    def __init__(self, export_dir: str = "exports")
    def export_json(self, data: dict, filename: str = None) -> str
    def export_csv(self, data: dict, filename: str = None) -> str
    def export_pdf(self, data: dict, visualizations: dict = None, filename: str = None) -> str
    def export_excel(self, data: dict, filename: str = None) -> str
    def get_export_history(self, limit: int = 10) -> list
```

**Exemplo de Uso:**

```python
from modules.export_manager import ExportManager

exporter = ExportManager()

# Exportar para JSON
json_file = exporter.export_json(data, "relatorio_usuario")

# Exportar para PDF com visualizações
pdf_file = exporter.export_pdf(
    data=analysis_data,
    visualizations=charts,
    filename="relatorio_completo"
)

# Histórico de exportações
history = exporter.get_export_history()
```

### 6. Cache Manager (`cache_manager.py`)

#### Classe: `CacheManager`

```python
class CacheManager:
    def __init__(self, cache_dir: str = "cache", ttl: int = 3600)
    def get(self, key: str) -> any
    def set(self, key: str, value: any, ttl: int = None) -> bool
    def delete(self, key: str) -> bool
    def clear(self) -> bool
    def get_stats(self) -> dict
```

**Exemplo de Uso:**

```python
from modules.cache_manager import CacheManager

cache = CacheManager(ttl=1800)  # 30 minutos

# Armazenar dados
cache.set("user_instagram_data", user_data, ttl=3600)

# Recuperar dados
cached_data = cache.get("user_instagram_data")

# Estatísticas do cache
stats = cache.get_stats()
print(f"Cache hits: {stats['hits']}, misses: {stats['misses']}")
```

### 7. Tkinter Visualizations (`tkinter_visualizations.py`)

#### Classe: `TkinterVisualizationManager`

```python
class TkinterVisualizationManager:
    def __init__(self, parent_frame)
    def create_engagement_comparison_chart(self, data: dict) -> tk.Frame
    def create_growth_metrics_chart(self, data: dict) -> tk.Frame
    def create_content_distribution_chart(self, data: dict) -> tk.Frame
    def create_comprehensive_dashboard(self, data: dict) -> tk.Frame
    def clear_visualizations(self)
```

**Exemplo de Uso:**

```python
import tkinter as tk
from modules.tkinter_visualizations import TkinterVisualizationManager

root = tk.Tk()
frame = tk.Frame(root)
viz_manager = TkinterVisualizationManager(frame)

# Criar gráfico de engajamento
engagement_chart = viz_manager.create_engagement_comparison_chart(data)
engagement_chart.pack(fill="both", expand=True)
```

## Estruturas de Dados

### Dados do Usuário (Padrão)

```python
user_data = {
    "platform": "instagram",
    "username": "exemplo_usuario",
    "profile": {
        "full_name": "Nome Completo",
        "biography": "Biografia",
        "followers_count": 1500,
        "following_count": 300,
        "posts_count": 120,
        "is_private": False,
        "is_verified": False,
        "profile_pic_url": "https://...",
        "external_url": "https://..."
    },
    "metrics": {
        "engagement_rate": 0.045,
        "avg_likes": 68,
        "avg_comments": 12,
        "posting_frequency": 0.8
    },
    "posts": [
        {
            "id": "post_id",
            "caption": "Legenda do post",
            "likes_count": 85,
            "comments_count": 15,
            "timestamp": "2025-01-15T10:30:00Z",
            "media_type": "photo"
        }
    ]
}
```

### Dados de Análise Cross-Platform

```python
cross_analysis = {
    "engagement_comparison": {
        "instagram": 0.045,
        "twitter": 0.032,
        "facebook": 0.028
    },
    "audience_overlap": {
        "instagram_twitter": 0.15,
        "instagram_facebook": 0.22,
        "twitter_facebook": 0.08
    },
    "content_patterns": {
        "posting_times": {
            "instagram": ["18:00", "20:00"],
            "twitter": ["12:00", "15:00"]
        },
        "content_types": {
            "instagram": {"photo": 0.7, "video": 0.3},
            "twitter": {"text": 0.8, "media": 0.2}
        }
    }
}
```

## Tratamento de Erros

### Exceções Personalizadas

```python
class APINotAvailableError(Exception):
    """Levantada quando uma API não está disponível"""
    pass

class RateLimitError(Exception):
    """Levantada quando o rate limit é atingido"""
    pass

class AuthenticationError(Exception):
    """Levantada quando há problemas de autenticação"""
    pass

class UserNotFoundError(Exception):
    """Levantada quando o usuário não é encontrado"""
    pass
```

### Exemplo de Tratamento

```python
try:
    user_info = instagram_api.get_user_info("username")
except UserNotFoundError:
    print("Usuário não encontrado")
except RateLimitError:
    print("Rate limit atingido, aguarde")
except AuthenticationError:
    print("Erro de autenticação, verifique credenciais")
except Exception as e:
    print(f"Erro inesperado: {e}")
```

## Configuração e Inicialização

### Exemplo de Configuração Completa

```python
import os
from dotenv import load_dotenv
from modules.instagram_api import InstagramAPI
from modules.facebook_api import FacebookAPI
from modules.twitter_api import TwitterAPI
from modules.cross_platform_analyzer import CrossPlatformAnalyzer
from modules.export_manager import ExportManager
from modules.cache_manager import CacheManager

# Carregar variáveis de ambiente
load_dotenv()

# Inicializar APIs
instagram_api = InstagramAPI(
    username=os.getenv('INSTAGRAM_USERNAME'),
    password=os.getenv('INSTAGRAM_PASSWORD')
)

facebook_api = FacebookAPI(
    app_id=os.getenv('FACEBOOK_APP_ID'),
    app_secret=os.getenv('FACEBOOK_APP_SECRET'),
    access_token=os.getenv('FACEBOOK_ACCESS_TOKEN')
)

twitter_api = TwitterAPI(
    api_key=os.getenv('TWITTER_API_KEY'),
    api_secret=os.getenv('TWITTER_API_SECRET'),
    access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
)

# Inicializar outros componentes
analyzer = CrossPlatformAnalyzer()
export_manager = ExportManager()
cache_manager = CacheManager()

# Verificar disponibilidade das APIs
available_apis = {
    'instagram': instagram_api.is_available(),
    'facebook': facebook_api.is_available(),
    'twitter': twitter_api.is_available()
}

print(f"APIs disponíveis: {available_apis}")
```

## Extensibilidade

### Adicionando Nova Plataforma

1. **Criar novo arquivo de API** (ex: `youtube_api.py`):

```python
class YouTubeAPI:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    
    def get_user_info(self, username: str) -> dict:
        # Implementar lógica específica do YouTube
        pass
    
    def is_available(self) -> bool:
        return self.api_key is not None
```

2. **Integrar no analisador cross-platform**:

```python
# Em cross_platform_analyzer.py
from modules.youtube_api import YouTubeAPI

class CrossPlatformAnalyzer:
    def __init__(self):
        # ... outras APIs
        self.youtube_api = YouTubeAPI(os.getenv('YOUTUBE_API_KEY'))
```

3. **Adicionar na interface**:

```python
# Em tkinter_app.py
self.youtube_var = tk.BooleanVar()
self.youtube_check = ttk.Checkbutton(
    platform_frame, 
    text="YouTube", 
    variable=self.youtube_var
)
```

## Boas Práticas

### 1. Rate Limiting

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Implementar lógica de rate limiting
            time.sleep(60 / calls_per_minute)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class InstagramAPI:
    @rate_limit(calls_per_minute=30)
    def get_user_info(self, username: str) -> dict:
        # Implementação do método
        pass
```

### 2. Logging

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class InstagramAPI:
    def get_user_info(self, username: str) -> dict:
        logger.info(f"Buscando informações do usuário: {username}")
        try:
            # Lógica da API
            logger.info(f"Dados obtidos com sucesso para: {username}")
        except Exception as e:
            logger.error(f"Erro ao buscar dados para {username}: {e}")
            raise
```

### 3. Validação de Dados

```python
from typing import Dict, Optional
from pydantic import BaseModel, validator

class UserProfile(BaseModel):
    username: str
    full_name: Optional[str]
    followers_count: int
    following_count: int
    posts_count: int
    
    @validator('followers_count', 'following_count', 'posts_count')
    def validate_counts(cls, v):
        if v < 0:
            raise ValueError('Contadores não podem ser negativos')
        return v
```

---

*Documentação da API atualizada em: Janeiro 2025*
*Versão: 2.0 (Tkinter)*