# reset_database.py
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from models.sistema_models import db
from main import app

def reset_database():
    """Reseta completamente a base de dados (CUIDADO: apaga todos os dados!)"""
    with app.app_context():
        try:
            # Apagar todas as tabelas
            db.drop_all()
            print("✅ Tabelas apagadas")
            
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas criadas")
            
            print("🔄 Base de dados resetada com sucesso!")
            print("💡 Agora execute o main.py para criar dados de exemplo")
            
        except Exception as e:
            print(f"❌ Erro ao resetar base de dados: {str(e)}")

if __name__ == '__main__':
    confirm = input("⚠️  TEM CUIDADO: Isto vai apagar TODOS os dados. Continuar? (s/N): ")
    if confirm.lower() == 's':
        reset_database()
    else:
        print("Operação cancelada")