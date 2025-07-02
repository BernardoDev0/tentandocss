from flask import current_app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """Inicializa o banco de dados com a aplicação Flask"""
    db.init_app(app)
    
    # Testar conexão
    try:
        with app.app_context():
            db.engine.connect()
            current_app.logger.info("✅ Conexão com o banco de dados estabelecida com sucesso!")
    except Exception as e:
        current_app.logger.error(f"❌ Falha na conexão com o banco de dados: {str(e)}")
        raise
    
    return db

# Importar modelos após definir db
from .employee import Employee
from .entry import Entry

# Exportar para facilitar importação
__all__ = ['db', 'Employee', 'Entry', 'init_db']

# Substituir as ocorrências de app.logger por current_app.logger