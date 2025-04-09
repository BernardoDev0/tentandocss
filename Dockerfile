FROM python:3.11-slim

# Instala dependências de sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ⚠️ Instala ferramentas completas de build do Python
RUN pip install --upgrade pip setuptools wheel

# Cria usuário não-root
RUN useradd -m myuser

# Define diretório de trabalho e copia os arquivos
WORKDIR /app
COPY --chown=myuser:myuser . .

# ⚠️ Instala as dependências (ainda como root)
RUN pip install --no-cache-dir -r requirements.txt

# Agora sim troca pro user seguro
USER myuser
ENV PATH="/home/myuser/.local/bin:${PATH}"

# Expõe a porta
EXPOSE 5000

# Comando do Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
