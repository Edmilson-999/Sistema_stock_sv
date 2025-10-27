import sqlite3
import os

def verificar_banco():
    db_path = "database/stock_management.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não existe!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Listar todas as tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()
    
    print("📊 Tabelas no banco de dados:")
    for tabela in tabelas:
        print(f"  - {tabela[0]}")
        
        # Mostrar estrutura de cada tabela
        cursor.execute(f"PRAGMA table_info({tabela[0]})")
        colunas = cursor.fetchall()
        print(f"    Colunas: {[coluna[1] for coluna in colunas]}")
    
    conn.close()

if __name__ == "__main__":
    verificar_banco()