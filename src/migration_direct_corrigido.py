# migration_direct_corrigido.py
import os
import sys
import sqlite3
from datetime import datetime

project_root = os.path.dirname(os.path.abspath(__file__))
database_path = os.path.join(project_root, 'database', 'app.db')

def migrar_directamente():
    """Migração direta usando SQLite3 - versão corrigida"""
    try:
        print("🚀 Migração direta da base de dados...")
        
        # Conectar à base de dados
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        # Verificar colunas existentes
        cursor.execute("PRAGMA table_info(beneficiarios)")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"🔍 Colunas atuais: {', '.join(columns)}")
        
        # Adicionar colunas se não existirem (sem DEFAULT para evitar erro)
        if 'instituicao_registro_id' not in columns:
            print("🔄 Adicionando instituicao_registro_id...")
            cursor.execute('''
                ALTER TABLE beneficiarios 
                ADD COLUMN instituicao_registro_id INTEGER
            ''')
        
        if 'data_registro' not in columns:
            print("🔄 Adicionando data_registro...")
            cursor.execute('''
                ALTER TABLE beneficiarios 
                ADD COLUMN data_registro DATETIME
            ''')
        
        # Encontrar ID da instituição admin
        cursor.execute("SELECT id, nome FROM instituicoes WHERE username IN ('admin', 'caritas') LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            instituicao_id, instituicao_nome = result
            print(f"🏢 Instituição admin encontrada: {instituicao_nome} (ID {instituicao_id})")
            
            # Atualizar beneficiários existentes
            cursor.execute("SELECT COUNT(*) FROM beneficiarios WHERE instituicao_registro_id IS NULL")
            count_sem_instituicao = cursor.fetchone()[0]
            
            if count_sem_instituicao > 0:
                print(f"🔄 Atribuindo {count_sem_instituicao} beneficiários à instituição admin...")
                
                # Atualizar instituicao_registro_id
                cursor.execute('''
                    UPDATE beneficiarios 
                    SET instituicao_registro_id = ?
                    WHERE instituicao_registro_id IS NULL
                ''', (instituicao_id,))
                
                # Atualizar data_registro para beneficiários sem data
                cursor.execute('''
                    UPDATE beneficiarios 
                    SET data_registro = datetime('now')
                    WHERE data_registro IS NULL
                ''')
                
                # Verificar resultado
                cursor.execute("SELECT COUNT(*) FROM beneficiarios WHERE instituicao_registro_id IS NOT NULL")
                count_com_instituicao = cursor.fetchone()[0]
                
                print(f"✅ {count_com_instituicao} beneficiários atribuídos à {instituicao_nome}")
        
        conn.commit()
        
        # Verificação final
        print("\n📊 Verificação final:")
        cursor.execute("SELECT COUNT(*) as total, COUNT(instituicao_registro_id) as com_instituicao, COUNT(data_registro) as com_data FROM beneficiarios")
        stats = cursor.fetchone()
        print(f"   - Total beneficiários: {stats[0]}")
        print(f"   - Com instituição: {stats[1]}")
        print(f"   - Com data registro: {stats[2]}")
        
        conn.close()
        
        print("🎉 Migração direta concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na migração direta: {str(e)}")
        return False

if __name__ == '__main__':
    if os.path.exists(database_path):
        migrar_directamente()
    else:
        print("❌ Base de dados não encontrada. Execute o main.py primeiro.")