#!/usr/bin/env python3
"""
Script de migração para adicionar instituicao_registro_id aos beneficiários existentes
Execute: python migration.py
"""

import os
import sys

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.dirname(__file__))

from models.sistema_models import db, Beneficiario, Instituicao
from main import app

def migrar_dados_existentes():
    """Atribui beneficiários existentes a uma instituição padrão (admin)"""# migration.py
import os
import sys

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.dirname(__file__))

from src.models.sistema_models import db, Beneficiario, Instituicao
from main import app

def migrar_dados_existentes():
    """Atribui beneficiários existentes a uma instituição padrão (admin)"""
    with app.app_context():
        try:
            # Verificar se existe alguma instituição admin
            instituicao_admin = Instituicao.query.filter(
                Instituicao.username.in_(['admin', 'caritas'])
            ).first()
            
            if not instituicao_admin:
                print("❌ Nenhuma instituição admin encontrada. Execute o main.py primeiro para criar dados de exemplo.")
                return False
            
            # Contar beneficiários existentes
            total_beneficiarios = Beneficiario.query.count()
            beneficiarios_sem_instituicao = Beneficiario.query.filter(
                Beneficiario.instituicao_registro_id.is_(None)
            ).count()
            
            print(f"📊 Estatísticas antes da migração:")
            print(f"   - Total de beneficiários: {total_beneficiarios}")
            print(f"   - Beneficiários sem instituição: {beneficiarios_sem_instituicao}")
            
            if beneficiarios_sem_instituicao > 0:
                # Atribuir beneficiários existentes à instituição admin
                Beneficiario.query.filter(
                    Beneficiario.instituicao_registro_id.is_(None)
                ).update({'instituicao_registro_id': instituicao_admin.id})
                
                db.session.commit()
                
                # Verificar resultados
                beneficiarios_migrados = Beneficiario.query.filter_by(
                    instituicao_registro_id=instituicao_admin.id
                ).count()
                
                print("✅ Migração concluída com sucesso!")
                print(f"📊 Estatísticas após migração:")
                print(f"   - Beneficiários migrados: {beneficiarios_migrados}")
                print(f"   - Instituição atribuída: {instituicao_admin.nome} (ID: {instituicao_admin.id})")
                return True
            else:
                print("ℹ️  Nenhum beneficiário precisa de migração - todos já têm instituição atribuída")
                return True
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro durante a migração: {str(e)}")
            return False

if __name__ == '__main__':
    print("🚀 Iniciando migração de beneficiários...")
    
    # Executar migração
    sucesso = migrar_dados_existentes()
    
    if sucesso:
        print("🎯 Migração concluída! Agora execute o main.py novamente.")
    else:
        print("💡 Execute o main.py primeiro para criar a base de dados e dados de exemplo.")
    with app.app_context():
        try:
            # Verificar se existe alguma instituição admin
            instituicao_admin = Instituicao.query.filter(
                Instituicao.username.in_(['admin', 'caritas'])
            ).first()
            
            if not instituicao_admin:
                # Criar uma instituição admin padrão se não existir
                instituicao_admin = Instituicao(
                    nome='Administrador do Sistema',
                    username='admin',
                    email='admin@sistema.com',
                    tipo_instituicao='governo',
                    responsavel='Administrador',
                    aprovada=True,
                    ativa=True
                )
                instituicao_admin.set_password('sv2024')
                db.session.add(instituicao_admin)
                db.session.commit()
                print("✅ Instituição admin criada")
            
            # Contar beneficiários existentes
            total_beneficiarios = Beneficiario.query.count()
            beneficiarios_sem_instituicao = Beneficiario.query.filter(
                Beneficiario.instituicao_registro_id.is_(None)
            ).count()
            
            print(f"📊 Estatísticas antes da migração:")
            print(f"   - Total de beneficiários: {total_beneficiarios}")
            print(f"   - Beneficiários sem instituição: {beneficiarios_sem_instituicao}")
            
            if beneficiarios_sem_instituicao > 0:
                # Atribuir beneficiários existentes à instituição admin
                Beneficiario.query.filter(
                    Beneficiario.instituicao_registro_id.is_(None)
                ).update({'instituicao_registro_id': instituicao_admin.id})
                
                db.session.commit()
                
                # Verificar resultados
                beneficiarios_migrados = Beneficiario.query.filter_by(
                    instituicao_registro_id=instituicao_admin.id
                ).count()
                
                print("✅ Migração concluída com sucesso!")
                print(f"📊 Estatísticas após migração:")
                print(f"   - Beneficiários migrados: {beneficiarios_migrados}")
                print(f"   - Instituição atribuída: {instituicao_admin.nome} (ID: {instituicao_admin.id})")
            else:
                print("ℹ️  Nenhum beneficiário precisa de migração - todos já têm instituição atribuída")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erro durante a migração: {str(e)}")
            raise

def verificar_migracao():
    """Verifica o estado da migração"""
    with app.app_context():
        try:
            # Estatísticas gerais
            total_beneficiarios = Beneficiario.query.count()
            beneficiarios_com_instituicao = Beneficiario.query.filter(
                Beneficiario.instituicao_registro_id.isnot(None)
            ).count()
            beneficiarios_sem_instituicao = Beneficiario.query.filter(
                Beneficiario.instituicao_registro_id.is_(None)
            ).count()
            
            print("🔍 Verificação da Migração:")
            print(f"   - Total de beneficiários: {total_beneficiarios}")
            print(f"   - Com instituição atribuída: {beneficiarios_com_instituicao}")
            print(f"   - Sem instituição atribuída: {beneficiarios_sem_instituicao}")
            
            # Distribuição por instituição
            from sqlalchemy import func
            distribuicao = db.session.query(
                Instituicao.nome,
                func.count(Beneficiario.nif).label('total')
            ).join(Beneficiario).group_by(Instituicao.id, Instituicao.nome).all()
            
            if distribuicao:
                print("   - Distribuição por instituição:")
                for instituicao_nome, total in distribuicao:
                    print(f"     • {instituicao_nome}: {total} beneficiários")
            
            return beneficiarios_sem_instituicao == 0
            
        except Exception as e:
            print(f"❌ Erro durante verificação: {str(e)}")
            return False

if __name__ == '__main__':
    print("🚀 Iniciando migração de beneficiários...")
    
    # Executar migração
    migrar_dados_existentes()
    
    print("\n" + "="*50)
    
    # Verificar migração
    sucesso = verificar_migracao()
    
    if sucesso:
        print("✅ Migração verificada com sucesso!")
    else:
        print("⚠️  A migração pode não ter sido completamente bem-sucedida")
    
    print("🎯 Próximos passos:")
    print("   1. As novas instituições registrarão seus próprios beneficiários")
    print("   2. Consultas cruzadas funcionarão para todos os beneficiários")
    print("   3. Cada instituição verá apenas seus próprios beneficiários por padrão")