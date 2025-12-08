import sqlite3
import os

def corrigir_constraint_movimentos():
    """
    Corrige a constraint NOT NULL da tabela movimentos_stock
    para permitir que instituicao_id seja NULL quando uma instituição é eliminada
    """
    print("🔧 Iniciando correção da constraint da tabela movimentos_stock...")
    
    db_path = "database/stock_management.db"
    
    # Verificar se o banco de dados existe
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Verificar a estrutura atual da tabela
        print("📋 Verificando estrutura atual...")
        cursor.execute("PRAGMA table_info(movimentos_stock)")
        colunas = cursor.fetchall()
        
        print("Colunas atuais da tabela movimentos_stock:")
        for coluna in colunas:
            print(f"  {coluna[1]} ({coluna[2]}) - NULL: {coluna[3]}, PK: {coluna[5]}")
        
        # 2. Contar registros atuais
        cursor.execute("SELECT COUNT(*) FROM movimentos_stock")
        total_registros = cursor.fetchone()[0]
        print(f"📊 Total de registros na tabela: {total_registros}")
        
        # 3. Criar tabela temporária com a estrutura CORRIGIDA
        print("🔄 Criando tabela temporária...")
        cursor.execute('''
            CREATE TABLE movimentos_stock_temp (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                tipo TEXT,
                quantidade INTEGER,
                data_movimento DATETIME NOT NULL,
                beneficiario_id INTEGER NOT NULL,
                instituicao_id INTEGER,  -- AGORA PODE SER NULL
                observacoes TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos (id),
                FOREIGN KEY (instituicao_id) REFERENCES instituicoes (id),
                FOREIGN KEY (beneficiario_id) REFERENCES beneficiarios (id)
            )
        ''')
        
        # 4. Copiar dados da tabela antiga para a nova (COM COLUNAS CORRETAS)
        print("📤 Copiando dados...")
        cursor.execute('''
            INSERT INTO movimentos_stock_temp 
            (id, produto_id, tipo, quantidade, data_movimento, 
             beneficiario_id, instituicao_id, observacoes)
            SELECT 
                id, produto_id, tipo, quantidade, data_movimento,
                beneficiario_id, instituicao_id, observacoes
            FROM movimentos_stock
        ''')
        
        # 5. Verificar se a cópia foi bem sucedida
        cursor.execute("SELECT COUNT(*) FROM movimentos_stock_temp")
        total_temp = cursor.fetchone()[0]
        print(f"✅ Dados copiados: {total_temp} registros")
        
        if total_temp != total_registros:
            print("❌ Número de registros não coincide! Abortando...")
            conn.rollback()
            return
        
        # 6. Remover tabela antiga
        print("🗑️ Removendo tabela antiga...")
        cursor.execute("DROP TABLE movimentos_stock")
        
        # 7. Renomear a nova tabela
        print("🔄 Renomeando tabela...")
        cursor.execute("ALTER TABLE movimentos_stock_temp RENAME TO movimentos_stock")
        
        # 8. Recriar índices se necessário
        print("📈 Recriando índices...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_movimentos_instituicao 
            ON movimentos_stock(instituicao_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_movimentos_produto 
            ON movimentos_stock(produto_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_movimentos_beneficiario 
            ON movimentos_stock(beneficiario_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_movimentos_data 
            ON movimentos_stock(data_movimento)
        ''')
        
        conn.commit()
        
        # 9. Verificar a nova estrutura
        print("📋 Verificando nova estrutura...")
        cursor.execute("PRAGMA table_info(movimentos_stock)")
        novas_colunas = cursor.fetchall()
        
        print("Nova estrutura da tabela movimentos_stock:")
        for coluna in novas_colunas:
            null_status = "PODE SER NULL" if coluna[3] else "NOT NULL"
            print(f"  {coluna[1]} ({coluna[2]}) - {null_status}")
        
        print("🎉 Correção concluída com sucesso!")
        print("💡 Agora a coluna instituicao_id pode ser NULL, permitindo a eliminação de instituições")
        
    except Exception as e:
        print(f"❌ Erro durante a correção: {e}")
        conn.rollback()
        print("🔙 Rollback executado - nenhuma alteração foi aplicada")
        
    finally:
        conn.close()

def limpar_tabela_temp():
    """Remove a tabela temporária se existir"""
    db_path = "database/stock_management.db"
    
    if not os.path.exists(db_path):
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se a tabela temporária existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movimentos_stock_temp'")
        if cursor.fetchone():
            print("🧹 Limpando tabela temporária...")
            cursor.execute("DROP TABLE movimentos_stock_temp")
            conn.commit()
            print("✅ Tabela temporária removida")
    except Exception as e:
        print(f"❌ Erro ao limpar tabela temporária: {e}")
    finally:
        conn.close()

def verificar_estado_banco():
    """Verifica o estado atual do banco de dados"""
    print("\n🔍 Verificando estado do banco de dados...")
    
    db_path = "database/stock_management.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        print("📊 Tabelas no banco de dados:")
        for tabela in tabelas:
            print(f"  - {tabela[0]}")
        
        # Verificar movimentos_stock especificamente
        cursor.execute("PRAGMA table_info(movimentos_stock)")
        colunas = cursor.fetchall()
        print("\n📋 Estrutura da tabela movimentos_stock:")
        for coluna in colunas:
            null_status = "PODE SER NULL" if coluna[3] else "NOT NULL"
            print(f"  {coluna[1]} ({coluna[2]}) - {null_status}")
        
        # Contar movimentos por instituição
        cursor.execute('''
            SELECT i.nome, COUNT(m.id) 
            FROM movimentos_stock m 
            LEFT JOIN instituicoes i ON m.instituicao_id = i.id 
            GROUP BY m.instituicao_id
        ''')
        movimentos_por_instituicao = cursor.fetchall()
        print("\n📦 Movimentos por instituição:")
        for instituicao_nome, count in movimentos_por_instituicao:
            print(f"  {instituicao_nome or 'NULL'}: {count} movimentos")
            
    except Exception as e:
        print(f"❌ Erro ao verificar banco: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🛠️  CORRETOR DE CONSTRAINT - MOVIMENTOS_STOCK")
    print("=" * 60)
    
    # Limpar tabela temporária se existir
    limpar_tabela_temp()
    
    # Verificar estado antes
    verificar_estado_banco()
    
    print("\n" + "=" * 60)
    input("⚠️  Pressione ENTER para iniciar a correção...")
    
    # Executar correção
    corrigir_constraint_movimentos()
    
    print("\n" + "=" * 60)
    print("✅ PROCESSO CONCLUÍDO")
    print("=" * 60)
    
    # Limpar tabela temporária novamente
    limpar_tabela_temp()
    
    # Verificar estado depois
    verificar_estado_banco()