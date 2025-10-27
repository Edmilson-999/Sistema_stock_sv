import sqlite3
import os

def migracao_final():
    print("🚀 Migração final da base de dados...")
    
    db_path = "database/stock_management.db"
    backup_path = "database/stock_management_backup.db"
    
    try:
        # Fazer backup
        if os.path.exists(db_path):
            import shutil
            shutil.copy2(db_path, backup_path)
            print("📦 Backup criado")
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Criar nova tabela com estrutura correta
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS beneficiarios_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nif TEXT UNIQUE,
                nome TEXT NOT NULL,
                idade INTEGER,
                endereco TEXT,
                contacto TEXT,
                num_agregado INTEGER,
                necessidades TEXT,
                observacoes TEXT,
                zona_residencia TEXT,
                perdas_pedidos TEXT,
                data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,               
                instituicao_registro_id INTEGER,
                FOREIGN KEY (instituicao_registro_id) REFERENCES instituicoes (id)
            )
        ''')
        
        # Copiar dados da tabela antiga para a nova
        cursor.execute('''
            INSERT INTO beneficiarios_new (
                id, nif, nome, idade, endereco, contacto, num_agregado,
                necessidades, observacoes, zona_residencia, perdas_pedidos,
                data_registro, instituicao_registro_id
            )
            SELECT 
                id, nif, nome, idade, endereco, contacto, num_agregado,
                necessidades, observacoes, zona_residencia, perdas_pedidos,
                COALESCE(datetime(data_registo), CURRENT_TIMESTAMP), instituicao_registro_id
            FROM beneficiarios
        ''')
        
        # Remover tabela antiga e renomear a nova
        cursor.execute("DROP TABLE beneficiarios")
        cursor.execute("ALTER TABLE beneficiarios_new RENAME TO beneficiarios")
        
        conn.commit()
        print("🎉 Migração final concluída com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migracao_final()