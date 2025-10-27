import sqlite3

def adicionar_data_registro():
    conn = sqlite3.connect('database/stock_management.db')
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna já existe
        cursor.execute("PRAGMA table_info(beneficiarios)")
        colunas = [coluna[1] for coluna in cursor.fetchall()]
        
        if 'data_registro' not in colunas:
            print("➕ Adicionando coluna data_registro...")
            cursor.execute("ALTER TABLE beneficiarios ADD COLUMN data_registro DATETIME")
            print("✅ Coluna data_registro adicionada com sucesso!")
            
            # Atualizar registros existentes com data atual
            cursor.execute("UPDATE beneficiarios SET data_registro = datetime('now') WHERE data_registro IS NULL")
            print("✅ Datas dos registros existentes atualizadas!")
        else:
            print("✅ Coluna data_registro já existe!")
        
        conn.commit()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        conn.rollback()
    finally:
        conn.close()

adicionar_data_registro()