import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.models.sistema_models import db, init_dados_exemplo
from src.routes.auth import auth_bp
from src.routes.beneficiarios import beneficiarios_bp
from src.routes.stock import stock_bp
from src.routes.dashboard import dashboard_bp
from src.routes.relatorios import relatorios_bp
from src.routes.alertas import alertas_bp
from dotenv import load_dotenv

# ========== CARREGAR VARIÁVEIS DO .ENV ==========
# Procura o arquivo .env na raiz do projeto
load_dotenv()

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# ========== CONFIGURAÇÕES DO SISTEMA ==========
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['FLASK_ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# ========== CONFIGURAÇÃO POSTGRESQL LOCAL ==========
# Lê as variáveis do arquivo .env
POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'sistema_stock_sv')

# Monta a string de conexão
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

# Configurações adicionais
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

# ==================================================

db.init_app(app)

# Registar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(beneficiarios_bp, url_prefix='/api/beneficiarios')
app.register_blueprint(stock_bp, url_prefix='/api/stock')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(alertas_bp, url_prefix='/api/alertas')
app.register_blueprint(relatorios_bp, url_prefix='/api/relatorios')

# Inicializar a base de dados
with app.app_context():
    try:
        db.create_all()
        print("✅ Tabelas criadas/verificadas com sucesso!")
        
        # Inicializar dados de exemplo
        init_dados_exemplo()
        print("✅ Dados de exemplo verificados/criados!")
        
        # Mostrar info da conexão (sem a password)
        print(f"📊 Conectado ao PostgreSQL: {POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
        
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        print("💡 Verifica se:")
        print("   1. O PostgreSQL está rodando (services.msc → PostgreSQL)")
        print("   2. As credenciais no .env estão corretas")
        print("   3. A base de dados 'sistema_stock_sv' existe (cria no pgAdmin)")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])