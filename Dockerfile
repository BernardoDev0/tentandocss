FROM python:3.10-slim-bullseye@sha256:1ba0dc5e5e668f5df0947b70e38e4a9d00e1c5e2e1d0aaf7a7a1f1a1a1a1a1a1

# Instala as dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Atualiza o pip para a versão mais recente
RUN pip install --upgrade pip

# Cria um usuário não-root para executar o aplicativo
RUN useradd -m myuser
USER myuser

# Adiciona /home/myuser/.local/bin ao PATH
ENV PATH="/home/myuser/.local/bin:${PATH}"

# Define o diretório de trabalho e copia os arquivos do projeto
WORKDIR /app
COPY --chown=myuser:myuser . .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta 5000
EXPOSE 5000

# Define o comando para rodar o aplicativo com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]