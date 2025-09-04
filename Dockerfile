# Dockerfile para Instagram Investigator
# Baseado em Python 3.11 com suporte a GUI via X11

FROM python:3.11-slim

# Metadados
LABEL maintainer="Instagram Investigator Team"
LABEL version="2.0"
LABEL description="Ferramenta de análise OSINT para Instagram com interface Tkinter"

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DISPLAY=:0

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    python3-tk \
    python3-dev \
    build-essential \
    libffi-dev \
    libssl-dev \
    libjpeg-dev \
    libpng-dev \
    libfreetype6-dev \
    pkg-config \
    x11-apps \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Cria usuário não-root
RUN useradd -m -s /bin/bash investigator

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos de dependências
COPY requirements.txt .
COPY requirements-test.txt .

# Instala dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-test.txt

# Copia código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p logs cache exports/csv exports/excel exports/json exports/pdf

# Define permissões
RUN chown -R investigator:investigator /app

# Muda para usuário não-root
USER investigator

# Expõe porta (se necessário para futuras funcionalidades web)
EXPOSE 8080

# Comando padrão
CMD ["python", "tkinter_app.py"]

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import tkinter; print('OK')" || exit 1