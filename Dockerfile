FROM python:3.11-slim

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Atualiza pip e instala wheel
RUN pip install --upgrade pip && pip install wheel

# Cria usuário não-root
RUN useradd -m myuser

# Define diretório de trabalho e copia os arquivos
WORKDIR /app
COPY --chown=myuser:myuser . .

# ⚠️ IMPORTANTE: instala as libs AQUI ainda como root (sem --user)
RUN pip install --no-cache-dir -r requirements.txt

# Agora sim muda para o usuário não-root
USER myuser
ENV PATH="/home/myuser/.local/bin:${PATH}"

# Expõe a porta usada pelo Gunicorn
EXPOSE 5000

# Comando para rodar o app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
