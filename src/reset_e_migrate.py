# reset_e_migrate.py
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from models.sistema_models import db
from main import app

def reset_e_migrate():
    """Reseta a base de dados e aplica a migração completa"""
    with app.app_context():
        try:
            print("⚠️  A resetar a base de dados...")
            
            # Apagar todas as tabelas
            db.drop_all()
            print("✅ Tabelas apagadas")
            
            # Criar todas as tabelas com a nova estrutura
            db.create_all()
            print("✅ Tabelas criadas com nova estrutura")
            
            # Inicializar dados de exemplo
            from src.models.sistema_models import init_dados_exemplo
            init_dados_exemplo()
            
            print("🎉 Base de dados resetada e migrada com sucesso!")
            print("💡 O sistema está pronto para usar as novas funcionalidades")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")

if __name__ == '__main__':
    confirm = input("⚠️  Isto vai apagar TODOS os dados existentes. Continuar? (s/N): ")
    if confirm.lower() == 's':
        reset_e_migrate()
    else:
        print("Operação cancelada")