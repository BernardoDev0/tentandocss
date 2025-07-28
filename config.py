import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # ================= Lógica de escolha de banco =================
    flask_env = os.getenv('FLASK_ENV', 'production').lower()

    if flask_env == 'development':
        # Ambiente local → usar SQLite (data.db na raiz)
        basedir = os.path.abspath(os.path.dirname(__file__))
        database_url = f"sqlite:///{os.path.join(basedir, 'data.db')}"
    else:
        # Produção → DATABASE_URL definido no Render
        database_url = os.getenv('DATABASE_URL', '')

        # Ajustar URL do Render se necessário
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
            database_url += "?sslmode=require" if '?' not in database_url else "&sslmode=require"
        elif not database_url:
            # Fallback de segurança (não deveria ocorrer em prod)
            basedir = os.path.abspath(os.path.dirname(__file__))
            database_url = f"sqlite:///{os.path.join(basedir, 'data.db')}"
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Timezone
    TIMEZONE = 'America/Sao_Paulo'
    
    # ================= Configurações de Email =================
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')