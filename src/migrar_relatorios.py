# migrar_relatorios.py
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import sqlite3

def criar_tabela_relatorios():
    """Cria a tabela de relatórios mensais diretamente com SQL"""
    
    db_path = "database/stock_management.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Banco de dados não encontrado em: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔍 Verificando tabelas existentes...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas_existentes = [t[0] for t in cursor.fetchall()]
        print(f"📊 Tabelas existentes: {tabelas_existentes}")
        
        if 'relatorios_mensais' in tabelas_existentes:
            print("✅ Tabela 'relatorios_mensais' já existe")
            
            # Verificar estrutura
            cursor.execute("PRAGMA table_info(relatorios_mensais)")
            colunas = cursor.fetchall()
            print("📋 Estrutura atual da tabela:")
            for coluna in colunas:
                print(f"  {coluna[1]} ({coluna[2]})")
            
            return True
        
        print("🔄 Criando tabela 'relatorios_mensais'...")
        
        # Criar tabela
        cursor.execute('''
            CREATE TABLE relatorios_mensais (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                instituicao_id INTEGER NOT NULL,
                ano INTEGER NOT NULL,
                mes INTEGER NOT NULL,
                data_geracao DATETIME,
                dados_json TEXT NOT NULL,
                total_entradas INTEGER DEFAULT 0,
                total_saidas INTEGER DEFAULT 0,
                saldo_mensal INTEGER DEFAULT 0,
                movimentos_count INTEGER DEFAULT 0,
                FOREIGN KEY (instituicao_id) REFERENCES instituicoes (id),
                UNIQUE(instituicao_id, ano, mes)
            )
        ''')
        
        # Criar índices para melhor performance
        cursor.execute('''
            CREATE INDEX idx_relatorios_instituicao 
            ON relatorios_mensais(instituicao_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX idx_relatorios_periodo 
            ON relatorios_mensais(ano, mes)
        ''')
        
        conn.commit()
        
        # Verificar criação
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas_novas = [t[0] for t in cursor.fetchall()]
        
        if 'relatorios_mensais' in tabelas_novas:
            print("✅ Tabela 'relatorios_mensais' criada com sucesso!")
            
            # Verificar estrutura criada
            cursor.execute("PRAGMA table_info(relatorios_mensais)")
            colunas = cursor.fetchall()
            print("📋 Estrutura da nova tabela:")
            for coluna in colunas:
                print(f"  {coluna[1]} ({coluna[2]})")
            
            return True
        else:
            print("❌ Falha ao criar tabela")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao criar tabela: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def verificar_banco_completo():
    """Verifica o estado completo do banco"""
    
    db_path = "database/stock_management.db"
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("\n🔍 VERIFICAÇÃO COMPLETA DO BANCO")
        print("=" * 50)
        
        # 1. Tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabelas = cursor.fetchall()
        print("\n📊 TABELAS NO BANCO:")
        for tabela in tabelas:
            print(f"  - {tabela[0]}")
        
        # 2. Verificar foreign keys
        print("\n🔗 VERIFICANDO INTEGRIDADE REFERENCIAL:")
        
        # Instituições
        cursor.execute("SELECT COUNT(*) FROM instituicoes")
        total_instituicoes = cursor.fetchone()[0]
        print(f"  Instituições: {total_instituicoes}")
        
        # Movimentos
        cursor.execute("SELECT COUNT(*) FROM movimentos_stock")
        total_movimentos = cursor.fetchone()[0]
        print(f"  Movimentos de stock: {total_movimentos}")
        
        # Relatórios (se existir)
        try:
            cursor.execute("SELECT COUNT(*) FROM relatorios_mensais")
            total_relatorios = cursor.fetchone()[0]
            print(f"  Relatórios mensais: {total_relatorios}")
        except:
            print(f"  Relatórios mensais: Tabela não existe")
        
        # 3. Verificar dados de exemplo
        print("\n📊 DADOS DE EXEMPLO:")
        
        cursor.execute("SELECT username, nome FROM instituicoes LIMIT 5")
        instituicoes = cursor.fetchall()
        print("  Primeiras instituições:")
        for username, nome in instituicoes:
            print(f"    - {nome} ({username})")
        
        cursor.execute('''
            SELECT m.id, p.nome, m.tipo, m.quantidade, m.data_movimento
            FROM movimentos_stock m
            JOIN produtos p ON m.produto_id = p.id
            LIMIT 5
        ''')
        movimentos = cursor.fetchall()
        print("  Primeiros movimentos:")
        for id, produto, tipo, quantidade, data in movimentos:
            print(f"    - {produto}: {quantidade} ({tipo}) em {data}")
            
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🛠️  MIGRAÇÃO - TABELA DE RELATÓRIOS MENSIAIS")
    print("=" * 60)
    
    # Verificar estado atual
    verificar_banco_completo()
    
    print("\n" + "=" * 60)
    input("⚠️  Pressione ENTER para criar a tabela de relatórios...")
    
    # Criar tabela
    sucesso = criar_tabela_relatorios()
    
    if sucesso:
        print("\n" + "=" * 60)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO")
        print("=" * 60)
        
        # Verificar estado final
        verificar_banco_completo()
    else:
        print("\n" + "=" * 60)
        print("❌ MIGRAÇÃO FALHOU")
        print("=" * 60)