import sqlite3
import os
from datetime import datetime

def recriar_banco_completo():
    print("🚀 Recriando banco de dados completo...")
    
    db_path = "database/stock_management.db"
    
    # Remover banco existente
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️  Banco antigo removido")
    
    # Criar diretório se não existir
    os.makedirs("database", exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Criar tabela instituicoes primeiro
    cursor.execute('''
        CREATE TABLE instituicoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            endereco TEXT,
            contacto TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar tabela beneficiarios
    cursor.execute('''
        CREATE TABLE beneficiarios (
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
    
    # Criar tabela produtos
    cursor.execute('''
        CREATE TABLE produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            categoria TEXT,
            quantidade INTEGER DEFAULT 0,
            unidade_medida TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Criar tabela movimentos_stock
    cursor.execute('''
        CREATE TABLE movimentos_stock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            tipo TEXT NOT NULL, -- 'entrada' ou 'saida'
            quantidade INTEGER NOT NULL,
            data_movimento DATETIME DEFAULT CURRENT_TIMESTAMP,
            beneficiario_id INTEGER,
            instituicao_id INTEGER,
            observacoes TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos (id),
            FOREIGN KEY (beneficiario_id) REFERENCES beneficiarios (id),
            FOREIGN KEY (instituicao_id) REFERENCES instituicoes (id)
        )
    ''')
    
    # Inserir dados de exemplo
    cursor.execute("INSERT INTO instituicoes (nome, endereco, contacto) VALUES (?, ?, ?)", 
                  ("Instituição A", "Endereço A", "123456789"))
    
    cursor.execute('''
        INSERT INTO beneficiarios 
        (nif, nome, idade, endereco, contacto, num_agregado, necessidades, zona_residencia, instituicao_registro_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("123456789", "João Silva", 35, "Rua A", "912345678", 4, "Alimentação", "Zona Norte", 1))
    
    cursor.execute("INSERT INTO produtos (nome, categoria, quantidade, unidade_medida) VALUES (?, ?, ?, ?)",
                  ("Arroz", "Alimentação", 100, "kg"))
    
    cursor.execute("INSERT INTO produtos (nome, categoria, quantidade, unidade_medida) VALUES (?, ?, ?, ?)",
                  ("Feijão", "Alimentação", 50, "kg"))
    
    conn.commit()
    
    # Verificar criação
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()
    
    print("✅ Tabelas criadas:")
    for tabela in tabelas:
        print(f"   - {tabela[0]}")
    
    conn.close()
    print("🎉 Banco de dados recriado com sucesso!")

if __name__ == "__main__":
    recriar_banco_completo()