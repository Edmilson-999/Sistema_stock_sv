import sqlite3

def verificar_estrutura_beneficiarios():
    conn = sqlite3.connect('database/stock_management.db')
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(beneficiarios)")
    colunas = cursor.fetchall()
    
    print("📋 Estrutura da tabela beneficiarios:")
    for coluna in colunas:
        print(f"  {coluna[1]} ({coluna[2]}) - PK: {coluna[5]}")
    
    conn.close()

verificar_estrutura_beneficiarios()