FROM python:3.11-slim

# Instala dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi-dev \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Atualiza o pip e instala wheel com root antes de mudar o usuário
RUN pip install --upgrade pip && pip install wheel

# Cria usuário não-root
RUN useradd -m myuser

# Define PATH e muda para o usuário myuser
ENV PATH="/home/myuser/.local/bin:${PATH}"
USER myuser

# Define diretório de trabalho e copia os arquivos
WORKDIR /app
COPY --chown=myuser:myuser . .

# Instala as dependências do projeto
RUN pip install --no-cache-dir --user -r requirements.txt

# Expõe a porta
EXPOSE 5000

# Comando padrão
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
