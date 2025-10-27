# migration_completa.py
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from models.sistema_models import db
from main import app

def migrar_tabelas():
    """Adiciona as novas colunas às tabelas existentes"""
    with app.app_context():
        try:
            # Verificar se a coluna já existe
            from sqlalchemy import inspect, text
            
            inspector = inspect(db.engine)
            columns_beneficiarios = [col['name'] for col in inspector.get_columns('beneficiarios')]
            
            print("🔍 Verificando estrutura da base de dados...")
            
            # Migração para beneficiarios
            if 'instituicao_registro_id' not in columns_beneficiarios:
                print("🔄 Adicionando coluna instituicao_registro_id à tabela beneficiarios...")
                db.session.execute(text('''
                    ALTER TABLE beneficiarios 
                    ADD COLUMN instituicao_registro_id INTEGER 
                    REFERENCES instituicoes(id)
                '''))
                print("✅ Coluna instituicao_registro_id adicionada")
            
            if 'data_registro' not in columns_beneficiarios:
                print("🔄 Adicionando coluna data_registro à tabela beneficiarios...")
                db.session.execute(text('''
                    ALTER TABLE beneficiarios 
                    ADD COLUMN data_registro DATETIME DEFAULT CURRENT_TIMESTAMP
                '''))
                print("✅ Coluna data_registro adicionada")
            
            db.session.commit()
            print("🎯 Migração da estrutura concluída!")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro durante migração: {str(e)}")
            return False

def migrar_dados():
    """Atribui beneficiários existentes a uma instituição padrão"""
    with app.app_context():
        try:
            from src.models.sistema_models import Beneficiario, Instituicao
            
            # Encontrar instituição admin
            instituicao_admin = Instituicao.query.filter(
                Instituicao.username.in_(['admin', 'caritas'])
            ).first()
            
            if not instituicao_admin:
                print("❌ Nenhuma instituição admin encontrada")
                return False
            
            # Contar beneficiários
            total_beneficiarios = Beneficiario.query.count()
            beneficiarios_sem_instituicao = Beneficiario.query.filter(
                Beneficiario.instituicao_registro_id.is_(None)
            ).count()
            
            print(f"📊 Estatísticas:")
            print(f"   - Total de beneficiários: {total_beneficiarios}")
            print(f"   - Beneficiários sem instituição: {beneficiarios_sem_instituicao}")
            
            if beneficiarios_sem_instituicao > 0:
                print(f"🔄 Atribuindo {beneficiarios_sem_instituicao} beneficiários à instituição admin...")
                
                # Atualizar beneficiários sem instituição
                Beneficiario.query.filter(
                    Beneficiario.instituicao_registro_id.is_(None)
                ).update({'instituicao_registro_id': instituicao_admin.id})
                
                db.session.commit()
                
                # Verificar
                beneficiarios_migrados = Beneficiario.query.filter_by(
                    instituicao_registro_id=instituicao_admin.id
                ).count()
                
                print(f"✅ {beneficiarios_migrados} beneficiários atribuídos à {instituicao_admin.nome}")
                return True
            else:
                print("ℹ️  Nenhum beneficiário precisa de migração")
                return True
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro durante migração de dados: {str(e)}")
            return False

if __name__ == '__main__':
    print("🚀 Iniciando migração completa...")
    
    # 1. Migrar estrutura
    if migrar_tabelas():
        # 2. Migrar dados
        if migrar_dados():
            print("🎉 Migração concluída com sucesso!")
            print("💡 Agora pode executar o sistema com as novas funcionalidades")
        else:
            print("⚠️  Migração de dados falhou")
    else:
        print("❌ Migração da estrutura falhou")