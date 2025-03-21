FROM python:3.10-slim

# Instala as dependências do sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Atualiza o pip para a versão mais recente
RUN pip install --upgrade pip

WORKDIR /app
COPY . .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]