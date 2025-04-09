FROM python:3.10-slim

# Instala dependências do sistema necessárias para compilar pacotes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Atualiza o pip e instala o wheel (necessário para alguns pacotes)
RUN pip install --upgrade pip && pip install wheel

# Cria um usuário não-root para rodar o app com mais segurança
RUN useradd -m myuser
USER myuser

# Define o PATH para incluir os pacotes instalados localmente
ENV PATH="/home/myuser/.local/bin:${PATH}"

# Define o diretório de trabalho e copia os arquivos do projeto
WORKDIR /app
COPY --chown=myuser:myuser . .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta usada pelo Gunicorn
EXPOSE 5000

# Comando para iniciar o app com Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
