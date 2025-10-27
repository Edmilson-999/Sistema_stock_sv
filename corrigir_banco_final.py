import sqlite3
import os

def corrigir_banco_final():
    print("🔧 Corrigindo estrutura do banco de dados...")
    
    db_path = "database/stock_management.db"
    backup_path = "database/stock_management_backup.db"
    
    # Fazer backup
    if os.path.exists(db_path):
        import shutil
        shutil.copy2(db_path, backup_path)
        print("📦 Backup criado")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar estrutura atual
        cursor.execute("PRAGMA table_info(beneficiarios)")
        colunas = cursor.fetchall()
        print("📋 Estrutura atual da tabela beneficiarios:")
        for coluna in colunas:
            print(f"  {coluna[1]} ({coluna[2]}) - PK: {coluna[5]}")
        
        # 2. Criar tabela temporária com estrutura correta
        cursor.execute('''
            CREATE TABLE beneficiarios_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nif TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                idade INTEGER,
                endereco TEXT,
                contacto TEXT,
                num_agregado INTEGER,
                necessidades TEXT,
                observacoes TEXT,
                zona_residencia TEXT,
                perdas_pedidos TEXT,
                instituicao_registro_id INTEGER,
                data_registro DATETIME,
                FOREIGN KEY (instituicao_registro_id) REFERENCES instituicoes (id)
            )
        ''')
        
        # 3. Copiar dados da tabela antiga para a nova
        cursor.execute('''
            INSERT INTO beneficiarios_temp 
            (nif, nome, idade, endereco, contacto, num_agregado, necessidades, 
             observacoes, zona_residencia, perdas_pedidos, instituicao_registro_id, data_registro)
            SELECT 
                nif, nome, idade, endereco, contacto, num_agregado, necessidades,
                observacoes, zona_residencia, perdas_pedidos, instituicao_registro_id,
                COALESCE(data_registro, datetime('now'))
            FROM beneficiarios
        ''')
        
        # 4. Remover tabela antiga e renomear a nova
        cursor.execute("DROP TABLE beneficiarios")
        cursor.execute("ALTER TABLE beneficiarios_temp RENAME TO beneficiarios")
        
        conn.commit()
        print("✅ Estrutura da tabela beneficiarios corrigida!")
        
        # 5. Verificar estrutura final
        cursor.execute("PRAGMA table_info(beneficiarios)")
        colunas_finais = cursor.fetchall()
        print("📋 Estrutura final da tabela beneficiarios:")
        for coluna in colunas_finais:
            print(f"  {coluna[1]} ({coluna[2]}) - PK: {coluna[5]}")
        
    except Exception as e:
        print(f"❌ Erro ao corrigir banco: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    corrigir_banco_final()