import sqlite3
import os

def verificar_e_corrigir_tudo():
    """Verifica e corrige completamente o banco para permitir eliminação de instituições"""
    
    db_path = "database/stock_management.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔍 VERIFICAÇÃO COMPLETA DO BANCO")
        print("=" * 50)
        
        # 1. Verificar estrutura das tabelas
        print("\n📋 ESTRUTURA DAS TABELAS:")
        
        tabelas = ['instituicoes', 'movimentos_stock', 'beneficiarios']
        for tabela in tabelas:
            cursor.execute(f"PRAGMA table_info({tabela})")
            colunas = cursor.fetchall()
            print(f"\n{tabela.upper()}:")
            for coluna in colunas:
                null_status = "NULL" if coluna[3] else "NOT NULL"
                print(f"  {coluna[1]} ({coluna[2]}) - {null_status}")
        
        # 2. Verificar foreign keys
        print("\n🔗 VERIFICANDO FOREIGN KEYS:")
        cursor.execute("PRAGMA foreign_key_list(movimentos_stock)")
        fks = cursor.fetchall()
        print("Foreign keys em movimentos_stock:")
        for fk in fks:
            print(f"  {fk[3]} -> {fk[2]}.{fk[4]}")
        
        # 3. Verificar dados
        print("\n📊 DADOS ATUAIS:")
        
        # Movimentos por instituição
        cursor.execute('''
            SELECT i.id, i.nome, COUNT(m.id) as total_movimentos
            FROM movimentos_stock m 
            JOIN instituicoes i ON m.instituicao_id = i.id 
            GROUP BY m.instituicao_id
        ''')
        movimentos = cursor.fetchall()
        print("Movimentos por instituição:")
        for inst_id, nome, count in movimentos:
            print(f"  {nome} (ID: {inst_id}): {count} movimentos")
        
        # Beneficiários por instituição
        cursor.execute('''
            SELECT i.id, i.nome, COUNT(b.nif) as total_beneficiarios
            FROM beneficiarios b 
            JOIN instituicoes i ON b.instituicao_registro_id = i.id 
            GROUP BY b.instituicao_registro_id
        ''')
        beneficiarios = cursor.fetchall()
        print("\nBeneficiários por instituição:")
        for inst_id, nome, count in beneficiarios:
            print(f"  {nome} (ID: {inst_id}): {count} beneficiários")
        
        print("\n✅ VERIFICAÇÃO CONCLUÍDA")
        print("\n💡 RECOMENDAÇÕES:")
        if any(count > 0 for _, _, count in movimentos):
            print("  - Há movimentos associados a instituições")
            print("  - Use a nova rota de eliminação que define instituicao_id como NULL")
        
        if any(count > 0 for _, _, count in beneficiarios):
            print("  - Há beneficiários associados a instituições") 
            print("  - A eliminação irá transferi-los para a instituição admin")
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verificar_e_corrigir_tudo()