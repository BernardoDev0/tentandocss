import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    
    # Configuração do banco - Render PostgreSQL
    database_url = os.getenv('DATABASE_URL', '')
    
    # Ajustar URL do Render se necessário
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
        database_url += "?sslmode=require" if '?' not in database_url else "&sslmode=require"
    elif not database_url:
        # Fallback apenas para desenvolvimento local
        basedir = os.path.abspath(os.path.dirname(__file__))
        database_url = f"sqlite:///{os.path.join(basedir, 'instance', 'app.db')}"
    
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Timezone
    TIMEZONE = 'America/Sao_Paulo'