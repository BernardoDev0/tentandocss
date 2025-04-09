FROM python:3.11-slim

# Instala dependências de sistema necessárias para compilar pacotes
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Atualiza o pip e instala o wheel
RUN pip install --upgrade pip && pip install wheel

# Cria usuário não-root
RUN useradd -m myuser
USER myuser

# Adiciona ~/.local/bin ao PATH
ENV PATH="/home/myuser/.local/bin:${PATH}"

# Define diretório do app e copia os arquivos
WORKDIR /app
COPY --chown=myuser:myuser . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta
EXPOSE 5000

# Comando padrão para iniciar o app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
