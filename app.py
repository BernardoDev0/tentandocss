from flask import Flask, request, render_template
from config import Config
from flask_caching import Cache
from flask_mail import Mail
from models import db
from utils.helpers import safe_json_dumps
import time
import os

# Instanciar cache antes das rotas
cache = Cache()

# Criar aplicação Flask
app = Flask(__name__)
app.config.from_object(Config)

# Config padrão de cache
app.config.setdefault('CACHE_TYPE', 'simple')
app.config.setdefault('CACHE_DEFAULT_TIMEOUT', 30)

# Inicializar extensões
cache.init_app(app)
mail = Mail(app)
db.init_app(app)

# Importar blueprints após cache existir
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.api import api_bp
from routes.diagnostics import diagnostics_bp

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(api_bp)
app.register_blueprint(diagnostics_bp)

# Adicionar função auxiliar ao contexto do template
app.jinja_env.globals.update(safe_json_dumps=safe_json_dumps)

# Criar tabelas se não existirem
with app.app_context():
    try:
        db.create_all()
        app.logger.info("Tabelas criadas com sucesso")
    except Exception as e:
        app.logger.error(f"Erro ao criar tabelas: {str(e)}")

# Tornar cache acessível via current_app.cache
app.cache = cache

@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request_time(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        app.logger.info(f"[DEBUG] {request.method} {request.path} levou {duration:.4f} segundos")
    return response

if __name__ == '__main__':
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', debug=debug_mode)