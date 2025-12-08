"""
Serviço para geração e gestão de relatórios mensais
"""

from datetime import datetime, timedelta
from src.models.sistema_models import db, MovimentoStock, ItemStock, Beneficiario, Instituicao, RelatorioMensal
from sqlalchemy import func, and_
import json

class RelatorioService: 
    """Serviço para geração de relatórios mensais"""
    
    @staticmethod
    def gerar_relatorio_mensal(instituicao_id, ano, mes):
        """
        Gera ou atualiza o relatório mensal para uma instituição
        
        Args:
            instituicao_id (int): ID da instituição
            ano (int): Ano do relatório
            mes (int): Mês do relatório (1-12)
            
        Returns:
            dict: Relatório completo
        """
        try:
            # Calcular datas do mês
            data_inicio = datetime(ano, mes, 1)
            if mes == 12:
                data_fim = datetime(ano + 1, 1, 1)
            else:
                data_fim = datetime(ano, mes + 1, 1)
            
            print(f"🔍 Gerando relatório para {mes}/{ano}")
            print(f"   Data início: {data_inicio}")
            print(f"   Data fim: {data_fim}")
            print(f"   Instituição ID: {instituicao_id}")
            
            # Buscar movimentos do mês usando a coluna correta 'data'
            movimentos = MovimentoStock.query.filter(
                MovimentoStock.instituicao_id == instituicao_id,
                MovimentoStock.data >= data_inicio,
                MovimentoStock.data < data_fim
            ).order_by(MovimentoStock.data.asc()).all()
            
            print(f"📊 Total de movimentos encontrados: {len(movimentos)}")
            
            if len(movimentos) == 0:
                print("ℹ️ Nenhum movimento encontrado para este período")
                return {
                    'sucesso': True,
                    'relatorio': RelatorioService.criar_relatorio_vazio(instituicao_id, ano, mes),
                    'estatisticas_salvar': {
                        'total_entradas': 0,
                        'total_saidas': 0,
                        'saldo_mensal': 0,
                        'movimentos_count': 0
                    }
                }
            
            # Separar entradas e saídas (usando tipo_movimento)
            entradas = [m for m in movimentos if m.tipo_movimento == 'entrada']
            saidas = [m for m in movimentos if m.tipo_movimento == 'saida']
            
            print(f"📥 Entradas: {len(entradas)}")
            print(f"📤 Saídas: {len(saidas)}")
            
            # Calcular totais
            total_entradas = sum(e.quantidade for e in entradas)
            total_saidas = sum(s.quantidade for s in saidas)
            saldo_mensal = total_entradas - total_saidas
            
            # Agrupar por item
            entradas_por_item = {}
            saidas_por_item = {}
            
            for entrada in entradas:
                try:
                    item_nome = entrada.item.nome if entrada.item else "Item não especificado"
                    unidade = entrada.item.unidade if entrada.item else "unidade"
                    
                    if item_nome not in entradas_por_item:
                        entradas_por_item[item_nome] = {'quantidade': 0, 'unidade': unidade}
                    entradas_por_item[item_nome]['quantidade'] += entrada.quantidade
                except Exception as e:
                    print(f"⚠️ Erro ao processar entrada {entrada.id}: {e}")
                    continue
            
            for saida in saidas:
                try:
                    item_nome = saida.item.nome if saida.item else "Item não especificado"
                    unidade = saida.item.unidade if saida.item else "unidade"
                    
                    if item_nome not in saidas_por_item:
                        saidas_por_item[item_nome] = {'quantidade': 0, 'unidade': unidade}
                    saidas_por_item[item_nome]['quantidade'] += saida.quantidade
                except Exception as e:
                    print(f"⚠️ Erro ao processar saída {saida.id}: {e}")
                    continue
            
            # Beneficiários atendidos
            beneficiarios_atendidos = set()
            for saida in saidas:
                try:
                    if saida.beneficiario:
                        beneficiarios_atendidos.add(saida.beneficiario.nome)
                except Exception as e:
                    print(f"⚠️ Erro ao processar beneficiário da saída {saida.id}: {e}")
                    continue
            
            # Construir relatório
            relatorio = {
                'cabecalho': {
                    'instituicao_id': instituicao_id,
                    'ano': ano,
                    'mes': mes,
                    'mes_nome': RelatorioService.get_mes_nome(mes),
                    'data_inicio': data_inicio.strftime('%Y-%m-%d'),
                    'data_fim': data_fim.strftime('%Y-%m-%d'),
                    'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                
                'resumo': {
                    'total_movimentos': len(movimentos),
                    'total_entradas': len(entradas),
                    'total_saidas': len(saidas),
                    'quantidade_total_entradas': float(total_entradas),
                    'quantidade_total_saidas': float(total_saidas),
                    'saldo_mensal': float(saldo_mensal),
                    'beneficiarios_atendidos': len(beneficiarios_atendidos)
                },
                
                'entradas': {
                    'lista': [
                        {
                            'id': e.id,
                            'data': e.data.strftime('%d/%m/%Y %H:%M') if e.data else 'Data não disponível',
                            'item': e.item.nome if e.item else 'Item não especificado',
                            'quantidade': float(e.quantidade),
                            'unidade': e.item.unidade if e.item else 'unidade',
                            'origem': e.origem_doacao or e.motivo or 'Não especificado',
                            'observacoes': e.observacoes
                        }
                        for e in entradas
                    ],
                    'por_item': entradas_por_item
                },
                
                'saidas': {
                    'lista': [
                        {
                            'id': s.id,
                            'data': s.data.strftime('%d/%m/%Y %H:%M') if s.data else 'Data não disponível',
                            'item': s.item.nome if s.item else 'Item não especificado',
                            'quantidade': float(s.quantidade),
                            'unidade': s.item.unidade if s.item else 'unidade',
                            'beneficiario': s.beneficiario.nome if s.beneficiario else 'Não especificado',
                            'beneficiario_nif': s.beneficiario.nif if s.beneficiario else '',
                            'motivo': s.motivo,
                            'local_entrega': s.local_entrega,
                            'observacoes': s.observacoes
                        }
                        for s in saidas
                    ],
                    'por_item': saidas_por_item
                },
                
                'estatisticas': {
                    'itens_movimentados': list(set(list(entradas_por_item.keys()) + list(saidas_por_item.keys()))),
                    'top_5_itens_entrada': sorted(
                        [(k, v) for k, v in entradas_por_item.items()], 
                        key=lambda x: x[1]['quantidade'], 
                        reverse=True
                    )[:5],
                    'top_5_itens_saida': sorted(
                        [(k, v) for k, v in saidas_por_item.items()], 
                        key=lambda x: x[1]['quantidade'], 
                        reverse=True
                    )[:5],
                    'beneficiarios_atendidos_lista': list(beneficiarios_atendidos),
                    'media_mensal': {
                        'entradas_por_dia': round(len(entradas) / 30, 1) if len(entradas) > 0 else 0,
                        'saidas_por_dia': round(len(saidas) / 30, 1) if len(saidas) > 0 else 0
                    }
                }
            }
            
            print(f"✅ Relatório gerado com sucesso!")
            print(f"   Movimentos: {len(movimentos)}")
            print(f"   Itens diferentes: {len(relatorio['estatisticas']['itens_movimentados'])}")
            print(f"   Beneficiários atendidos: {len(beneficiarios_atendidos)}")
            
            return {
                'sucesso': True,
                'relatorio': relatorio,
                'estatisticas_salvar': {
                    'total_entradas': float(total_entradas),
                    'total_saidas': float(total_saidas),
                    'saldo_mensal': float(saldo_mensal),
                    'movimentos_count': len(movimentos)
                }
            }
            
        except Exception as e:
            print(f"❌ Erro ao gerar relatório: {str(e)}")
            import traceback
            print(f"🔍 Stack trace: {traceback.format_exc()}")
            return {
                'sucesso': False,
                'erro': f'Erro ao gerar relatório: {str(e)}'
            }
    
    @staticmethod
    def criar_relatorio_vazio(instituicao_id, ano, mes):
        """Cria um relatório vazio quando não há dados"""
        return {
            'cabecalho': {
                'instituicao_id': instituicao_id,
                'ano': ano,
                'mes': mes,
                'mes_nome': RelatorioService.get_mes_nome(mes),
                'data_inicio': f'{ano}-{mes:02d}-01',
                'data_fim': f'{ano}-{mes+1:02d}-01' if mes < 12 else f'{ano+1}-01-01',
                'data_geracao': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            
            'resumo': {
                'total_movimentos': 0,
                'total_entradas': 0,
                'total_saidas': 0,
                'quantidade_total_entradas': 0,
                'quantidade_total_saidas': 0,
                'saldo_mensal': 0,
                'beneficiarios_atendidos': 0
            },
            
            'entradas': {
                'lista': [],
                'por_item': {}
            },
            
            'saidas': {
                'lista': [],
                'por_item': {}
            },
            
            'estatisticas': {
                'itens_movimentados': [],
                'top_5_itens_entrada': [],
                'top_5_itens_saida': [],
                'beneficiarios_atendidos_lista': [],
                'media_mensal': {
                    'entradas_por_dia': 0,
                    'saidas_por_dia': 0
                }
            }
        }
    
    @staticmethod
    def salvar_relatorio_mensal(instituicao_id, ano, mes, relatorio_data, estatisticas):
        """
        Salva ou atualiza um relatório mensal no banco
        
        Returns:
            dict: Resultado da operação
        """
        try:
            # Verificar se já existe
            relatorio_existente = RelatorioMensal.query.filter_by(
                instituicao_id=instituicao_id,
                ano=ano,
                mes=mes
            ).first()
            
            if relatorio_existente:
                # Atualizar
                relatorio_existente.dados_json = json.dumps(relatorio_data)
                relatorio_existente.total_entradas = estatisticas['total_entradas']
                relatorio_existente.total_saidas = estatisticas['total_saidas']
                relatorio_existente.saldo_mensal = estatisticas['saldo_mensal']
                relatorio_existente.movimentos_count = estatisticas['movimentos_count']
                relatorio_existente.data_geracao = datetime.now()
                mensagem = 'Relatório atualizado'
            else:
                # Criar novo
                relatorio = RelatorioMensal(
                    instituicao_id=instituicao_id,
                    ano=ano,
                    mes=mes,
                    dados_json=json.dumps(relatorio_data),
                    total_entradas=estatisticas['total_entradas'],
                    total_saidas=estatisticas['total_saidas'],
                    saldo_mensal=estatisticas['saldo_mensal'],
                    movimentos_count=estatisticas['movimentos_count']
                )
                db.session.add(relatorio)
                mensagem = 'Relatório salvo'
            
            db.session.commit()
            
            return {
                'sucesso': True,
                'mensagem': mensagem
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'sucesso': False,
                'erro': f'Erro ao salvar relatório: {str(e)}'
            }
    
    @staticmethod
    def listar_relatorios_instituicao(instituicao_id):
        """
        Lista todos os relatórios de uma instituição
        
        Returns:
            list: Lista de relatórios ordenados por ano/mês
        """
        try:
            relatorios = RelatorioMensal.query.filter_by(
                instituicao_id=instituicao_id
            ).order_by(
                RelatorioMensal.ano.desc(),
                RelatorioMensal.mes.desc()
            ).all()
            
            return [r.to_dict() for r in relatorios]
            
        except Exception as e:
            return []
    
    @staticmethod
    def get_mes_nome(mes):
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        return meses[mes - 1] if 1 <= mes <= 12 else f'Mês {mes}'
    
    @staticmethod
    def get_meses_disponiveis(instituicao_id):
        """
        Retorna os meses/anos para os quais é possível gerar relatórios
        baseado nos movimentos existentes
        """
        try:
            # Buscar datas dos movimentos usando a coluna 'data'
            datas = db.session.query(
                func.strftime('%Y', MovimentoStock.data).label('ano'),
                func.strftime('%m', MovimentoStock.data).label('mes')
            ).filter(
                MovimentoStock.instituicao_id == instituicao_id
            ).distinct().order_by('ano', 'mes').all()
            
            periodos = []
            for ano_str, mes_str in datas:
                if ano_str and mes_str:
                    periodos.append({
                        'ano': int(ano_str),
                        'mes': int(mes_str),
                        'mes_nome': RelatorioService.get_mes_nome(int(mes_str))
                    })
            
            return periodos
            
        except Exception as e:
            print(f"⚠️ Erro ao obter períodos disponíveis: {e}")
            return []