from src.database import db
from src.main import create_app

def atualizar_banco():
    app = create_app()
    
    with app.app_context():
        try:
            # Isso vai garantir que todas as tabelas estejam sincronizadas com os modelos
            db.create_all()
            print("✅ Banco de dados sincronizado com os modelos!")
        except Exception as e:
            print(f"❌ Erro ao sincronizar banco: {e}")

if __name__ == "__main__":
    atualizar_banco()