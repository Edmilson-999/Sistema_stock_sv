import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from src.models.sistema_models import db, init_dados_exemplo
from src.routes.auth import auth_bp
from src.routes.beneficiarios import beneficiarios_bp
from src.routes.stock import stock_bp
from src.routes.dashboard import dashboard_bp
from src.routes.alertas import alertas_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'sistema_stock_sv_2024_enchente_sao_vicente'

# Registar blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(beneficiarios_bp, url_prefix='/api/beneficiarios')
app.register_blueprint(stock_bp, url_prefix='/api/stock')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(alertas_bp, url_prefix='/api/alertas')

# Configuração da base de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    # Inicializar dados de exemplo na primeira execução
    init_dados_exemplo()

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
    app.run(host='0.0.0.0', port=5000, debug=True)
