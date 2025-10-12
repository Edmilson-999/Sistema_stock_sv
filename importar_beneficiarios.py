#!/usr/bin/env python3
"""
Script para importar beneficiários de ficheiro Excel para o sistema de stock
Uso: python importar_beneficiarios.py caminho_para_ficheiro.xlsx
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from models.sistema_models import db, Beneficiario
from main import app

def limpar_dados(valor):
    """Limpa e valida dados vindos do Excel"""
    if pd.isna(valor) or valor == '' or str(valor).lower() in ['nan', 'none', 'null']:
        return None
    return str(valor).strip()

def importar_beneficiarios_excel(caminho_ficheiro, skiprows=0):
    """
    Importa beneficiários de um ficheiro Excel
    
    Args:
        caminho_ficheiro (str): Caminho para o ficheiro Excel
        skiprows (int): Número de linhas a saltar no início
    
    Returns:
        dict: Resultado da importação
    """
    
    if not os.path.exists(caminho_ficheiro):
        return {'sucesso': False, 'erro': f'Ficheiro não encontrado: {caminho_ficheiro}'}
    
    try:
        # Ler ficheiro Excel
        print(f"📖 A ler ficheiro: {caminho_ficheiro}")
        df = pd.read_excel(caminho_ficheiro, skiprows=skiprows)
        
        print(f"📊 Ficheiro carregado com {len(df)} linhas")
        print(f"📋 Colunas encontradas: {list(df.columns)}")
        
        # Mostrar primeiras linhas para o utilizador verificar
        print("\n🔍 Primeiras 3 linhas do ficheiro:")
        print(df.head(3).to_string())
        
        # Pedir ao utilizador para mapear as colunas
        print("\n📝 Por favor, indique qual coluna corresponde a cada campo:")
        print("(Deixe em branco se a coluna não existir)")
        
        mapeamento = {}
        campos = {
            'nif': 'NIF/Número de Identificação (obrigatório)',
            'nome': 'Nome completo (obrigatório)', 
            'idade': 'Idade',
            'contacto': 'Contacto/Telefone',
            'endereco': 'Endereço/Morada',
            'zona_residencia': 'Zona de residência',
            'num_agregado': 'Número de pessoas no agregado familiar',
            'necessidades': 'Necessidades específicas',
            'perdas_pedidos': 'Perdas/Pedidos',
            'observacoes': 'Observações'
        }
        
        for campo, descricao in campos.items():
            while True:
                resposta = input(f"{descricao}: ").strip()
                if resposta == '':
                    mapeamento[campo] = None
                    break
                elif resposta in df.columns:
                    mapeamento[campo] = resposta
                    break
                else:
                    print(f"❌ Coluna '{resposta}' não encontrada. Colunas disponíveis: {list(df.columns)}")
        
        # Verificar campos obrigatórios
        if not mapeamento.get('nif') or not mapeamento.get('nome'):
            return {'sucesso': False, 'erro': 'NIF e Nome são campos obrigatórios'}
        
        # Processar dados
        with app.app_context():
            beneficiarios_criados = 0
            beneficiarios_atualizados = 0
            erros = []
            
            for index, row in df.iterrows():
                try:
                    # Extrair dados baseado no mapeamento
                    nif = limpar_dados(row[mapeamento['nif']])
                    nome = limpar_dados(row[mapeamento['nome']])
                    
                    # Verificar campos obrigatórios
                    if not nif or not nome:
                        erros.append(f"Linha {index + skiprows + 2}: NIF ou Nome em falta")
                        continue
                    
                    # Verificar se beneficiário já existe
                    beneficiario_existente = Beneficiario.query.get(nif)
                    
                    if beneficiario_existente:
                        # Atualizar beneficiário existente
                        beneficiario_existente.nome = nome
                        if mapeamento.get('idade'):
                            idade_str = limpar_dados(row[mapeamento['idade']])
                            if idade_str and idade_str.isdigit():
                                beneficiario_existente.idade = int(idade_str)
                        
                        if mapeamento.get('contacto'):
                            beneficiario_existente.contacto = limpar_dados(row[mapeamento['contacto']])
                        
                        if mapeamento.get('endereco'):
                            beneficiario_existente.endereco = limpar_dados(row[mapeamento['endereco']])
                        
                        if mapeamento.get('zona_residencia'):
                            beneficiario_existente.zona_residencia = limpar_dados(row[mapeamento['zona_residencia']])
                        
                        if mapeamento.get('num_agregado'):
                            agregado_str = limpar_dados(row[mapeamento['num_agregado']])
                            if agregado_str and agregado_str.isdigit():
                                beneficiario_existente.num_agregado = int(agregado_str)
                        
                        if mapeamento.get('necessidades'):
                            beneficiario_existente.necessidades = limpar_dados(row[mapeamento['necessidades']])
                        
                        if mapeamento.get('perdas_pedidos'):
                            beneficiario_existente.perdas_pedidos = limpar_dados(row[mapeamento['perdas_pedidos']])
                        
                        if mapeamento.get('observacoes'):
                            beneficiario_existente.observacoes = limpar_dados(row[mapeamento['observacoes']])
                        
                        beneficiarios_atualizados += 1
                        
                    else:
                        # Criar novo beneficiário
                        dados_beneficiario = {
                            'nif': nif,
                            'nome': nome
                        }
                        
                        # Adicionar campos opcionais
                        if mapeamento.get('idade'):
                            idade_str = limpar_dados(row[mapeamento['idade']])
                            if idade_str and idade_str.isdigit():
                                dados_beneficiario['idade'] = int(idade_str)
                        
                        if mapeamento.get('contacto'):
                            dados_beneficiario['contacto'] = limpar_dados(row[mapeamento['contacto']])
                        
                        if mapeamento.get('endereco'):
                            dados_beneficiario['endereco'] = limpar_dados(row[mapeamento['endereco']])
                        
                        if mapeamento.get('zona_residencia'):
                            dados_beneficiario['zona_residencia'] = limpar_dados(row[mapeamento['zona_residencia']])
                        
                        if mapeamento.get('num_agregado'):
                            agregado_str = limpar_dados(row[mapeamento['num_agregado']])
                            if agregado_str and agregado_str.isdigit():
                                dados_beneficiario['num_agregado'] = int(agregado_str)
                        
                        if mapeamento.get('necessidades'):
                            dados_beneficiario['necessidades'] = limpar_dados(row[mapeamento['necessidades']])
                        
                        if mapeamento.get('perdas_pedidos'):
                            dados_beneficiario['perdas_pedidos'] = limpar_dados(row[mapeamento['perdas_pedidos']])
                        
                        if mapeamento.get('observacoes'):
                            dados_beneficiario['observacoes'] = limpar_dados(row[mapeamento['observacoes']])
                        
                        beneficiario = Beneficiario(**dados_beneficiario)
                        db.session.add(beneficiario)
                        beneficiarios_criados += 1
                
                except Exception as e:
                    erros.append(f"Linha {index + skiprows + 2}: {str(e)}")
                    continue
            
            # Confirmar alterações
            try:
                db.session.commit()
                
                resultado = {
                    'sucesso': True,
                    'beneficiarios_criados': beneficiarios_criados,
                    'beneficiarios_atualizados': beneficiarios_atualizados,
                    'total_processados': beneficiarios_criados + beneficiarios_atualizados,
                    'erros': erros
                }
                
                return resultado
                
            except Exception as e:
                db.session.rollback()
                return {'sucesso': False, 'erro': f'Erro ao guardar na base de dados: {str(e)}'}
    
    except Exception as e:
        return {'sucesso': False, 'erro': f'Erro ao processar ficheiro: {str(e)}'}

def main():
    """Função principal do script"""
    if len(sys.argv) < 2:
        print("❌ Uso: python importar_beneficiarios.py caminho_para_ficheiro.xlsx [linhas_a_saltar]")
        print("   Exemplo: python importar_beneficiarios.py dados/beneficiarios.xlsx 2")
        sys.exit(1)
    
    caminho_ficheiro = sys.argv[1]
    skiprows = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    
    print("🌱 Sistema de Importação de Beneficiários - São Vicente")
    print("=" * 60)
    
    resultado = importar_beneficiarios_excel(caminho_ficheiro, skiprows)
    
    if resultado['sucesso']:
        print("\n✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print(f"📊 Beneficiários criados: {resultado['beneficiarios_criados']}")
        print(f"🔄 Beneficiários atualizados: {resultado['beneficiarios_atualizados']}")
        print(f"📈 Total processados: {resultado['total_processados']}")
        
        if resultado['erros']:
            print(f"\n⚠️  Erros encontrados ({len(resultado['erros'])}):")
            for erro in resultado['erros'][:10]:  # Mostrar apenas os primeiros 10 erros
                print(f"   - {erro}")
            if len(resultado['erros']) > 10:
                print(f"   ... e mais {len(resultado['erros']) - 10} erros")
    else:
        print(f"\n❌ ERRO NA IMPORTAÇÃO: {resultado['erro']}")
        sys.exit(1)

if __name__ == '__main__':
    main()
