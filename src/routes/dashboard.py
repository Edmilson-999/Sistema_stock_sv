from flask import Blueprint, request, jsonify
from src.models.sistema_models import db, ItemStock, MovimentoStock, Beneficiario, Instituicao
from src.routes.auth import login_required, get_current_instituicao
from datetime import datetime, timedelta
from sqlalchemy import func, and_

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Endpoint para obter estatísticas gerais do dashboard"""
    try:
        instituicao = get_current_instituicao()
        
        # Estatísticas gerais do sistema (visíveis para todas as instituições)
        total_beneficiarios = Beneficiario.query.count()
        total_itens_stock = ItemStock.query.filter_by(ativo=True).count()
        
        # Beneficiários que receberam ajuda
        beneficiarios_com_ajuda = db.session.query(Beneficiario.nif).join(
            MovimentoStock, Beneficiario.nif == MovimentoStock.beneficiario_nif
        ).filter(MovimentoStock.tipo_movimento == 'saida').distinct().count()
        
        # Estatísticas específicas da instituição
        total_movimentos_instituicao = MovimentoStock.query.filter_by(
            instituicao_id=instituicao.id
        ).count()
        
        total_entradas_instituicao = db.session.query(func.sum(MovimentoStock.quantidade)).filter_by(
            instituicao_id=instituicao.id,
            tipo_movimento='entrada'
        ).scalar() or 0
        
        total_saidas_instituicao = db.session.query(func.sum(MovimentoStock.quantidade)).filter_by(
            instituicao_id=instituicao.id,
            tipo_movimento='saida'
        ).scalar() or 0
        
        # Beneficiários únicos atendidos por esta instituição
        beneficiarios_atendidos_instituicao = db.session.query(MovimentoStock.beneficiario_nif).filter_by(
            instituicao_id=instituicao.id,
            tipo_movimento='saida'
        ).distinct().count()
        
        # Movimentos recentes (últimos 7 dias)
        data_limite = datetime.utcnow() - timedelta(days=7)
        movimentos_recentes = MovimentoStock.query.filter(
            MovimentoStock.instituicao_id == instituicao.id,
            MovimentoStock.data >= data_limite
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'sistema': {
                    'total_beneficiarios': total_beneficiarios,
                    'beneficiarios_com_ajuda': beneficiarios_com_ajuda,
                    'beneficiarios_sem_ajuda': total_beneficiarios - beneficiarios_com_ajuda,
                    'total_itens_stock': total_itens_stock
                },
                'instituicao': {
                    'nome': instituicao.nome,
                    'total_movimentos': total_movimentos_instituicao,
                    'total_entradas': total_entradas_instituicao,
                    'total_saidas': total_saidas_instituicao,
                    'beneficiarios_atendidos': beneficiarios_atendidos_instituicao,
                    'movimentos_recentes': movimentos_recentes
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@dashboard_bp.route('/atividade-recente', methods=['GET'])
@login_required
def get_atividade_recente():
    """Endpoint para obter atividade recente da instituição"""
    try:
        instituicao = get_current_instituicao()
        limit = int(request.args.get('limit', 10))
        
        # Últimos movimentos da instituição
        movimentos_recentes = MovimentoStock.query.filter_by(
            instituicao_id=instituicao.id
        ).order_by(MovimentoStock.data.desc()).limit(limit).all()
        
        atividades = []
        for movimento in movimentos_recentes:
            atividade = {
                'id': movimento.id,
                'tipo': movimento.tipo_movimento,
                'item_nome': movimento.item.nome,
                'quantidade': movimento.quantidade,
                'unidade': movimento.item.unidade,
                'data': movimento.data.isoformat(),
                'motivo': movimento.motivo
            }
            
            if movimento.tipo_movimento == 'saida' and movimento.beneficiario:
                atividade['beneficiario_nome'] = movimento.beneficiario.nome
                atividade['beneficiario_nif'] = movimento.beneficiario_nif
            elif movimento.tipo_movimento == 'entrada':
                atividade['origem_doacao'] = movimento.origem_doacao
            
            atividades.append(atividade)
        
        return jsonify({
            'success': True,
            'atividades': atividades
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@dashboard_bp.route('/stock-resumo', methods=['GET'])
@login_required
def get_stock_resumo():
    """Endpoint para obter resumo do stock atual"""
    try:
        # Obter itens com stock disponível
        itens_com_stock = []
        itens = ItemStock.query.filter_by(ativo=True).all()
        
        for item in itens:
            stock_total = item.get_stock_total()
            if stock_total > 0:
                itens_com_stock.append({
                    'id': item.id,
                    'nome': item.nome,
                    'categoria': item.categoria,
                    'stock_total': stock_total,
                    'unidade': item.unidade
                })
        
        # Ordenar por categoria e nome
        itens_com_stock.sort(key=lambda x: (x['categoria'] or '', x['nome']))
        
        # Agrupar por categoria
        categorias = {}
        for item in itens_com_stock:
            categoria = item['categoria'] or 'Outros'
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append(item)
        
        return jsonify({
            'success': True,
            'stock_resumo': {
                'total_itens_disponiveis': len(itens_com_stock),
                'categorias': categorias
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@dashboard_bp.route('/graficos/movimentos-tempo', methods=['GET'])
@login_required
def get_graficos_movimentos_tempo():
    """Endpoint para obter dados para gráfico de movimentos ao longo do tempo"""
    try:
        instituicao = get_current_instituicao()
        dias = int(request.args.get('dias', 30))
        
        data_inicio = datetime.utcnow() - timedelta(days=dias)
        
        # Query para obter movimentos agrupados por data
        movimentos_por_data = db.session.query(
            func.date(MovimentoStock.data).label('data'),
            MovimentoStock.tipo_movimento,
            func.sum(MovimentoStock.quantidade).label('total_quantidade'),
            func.count(MovimentoStock.id).label('total_movimentos')
        ).filter(
            MovimentoStock.instituicao_id == instituicao.id,
            MovimentoStock.data >= data_inicio
        ).group_by(
            func.date(MovimentoStock.data),
            MovimentoStock.tipo_movimento
        ).all()
        
        # Organizar dados para o gráfico
        dados_grafico = {}
        for movimento in movimentos_por_data:
            data_str = movimento.data.strftime('%Y-%m-%d')
            if data_str not in dados_grafico:
                dados_grafico[data_str] = {
                    'data': data_str,
                    'entradas': 0,
                    'saidas': 0,
                    'entradas_count': 0,
                    'saidas_count': 0
                }
            
            if movimento.tipo_movimento == 'entrada':
                dados_grafico[data_str]['entradas'] = movimento.total_quantidade
                dados_grafico[data_str]['entradas_count'] = movimento.total_movimentos
            else:
                dados_grafico[data_str]['saidas'] = movimento.total_quantidade
                dados_grafico[data_str]['saidas_count'] = movimento.total_movimentos
        
        # Converter para lista ordenada
        dados_lista = list(dados_grafico.values())
        dados_lista.sort(key=lambda x: x['data'])
        
        return jsonify({
            'success': True,
            'dados_grafico': dados_lista
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@dashboard_bp.route('/graficos/categorias', methods=['GET'])
@login_required
def get_graficos_categorias():
    """Endpoint para obter dados para gráfico de distribuição por categorias"""
    try:
        instituicao = get_current_instituicao()
        
        # Movimentos por categoria (apenas saídas para ver o que foi distribuído)
        categorias_query = db.session.query(
            ItemStock.categoria,
            func.sum(MovimentoStock.quantidade).label('total_quantidade'),
            func.count(MovimentoStock.id).label('total_movimentos')
        ).join(
            MovimentoStock, ItemStock.id == MovimentoStock.item_id
        ).filter(
            MovimentoStock.instituicao_id == instituicao.id,
            MovimentoStock.tipo_movimento == 'saida'
        ).group_by(ItemStock.categoria).all()
        
        dados_categorias = []
        for categoria_data in categorias_query:
            dados_categorias.append({
                'categoria': categoria_data.categoria or 'Outros',
                'quantidade': categoria_data.total_quantidade,
                'movimentos': categoria_data.total_movimentos
            })
        
        # Ordenar por quantidade (maior para menor)
        dados_categorias.sort(key=lambda x: x['quantidade'], reverse=True)
        
        return jsonify({
            'success': True,
            'dados_categorias': dados_categorias
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@dashboard_bp.route('/relatorio/mensal', methods=['GET'])
@login_required
def get_relatorio_mensal():
    """Endpoint para obter relatório mensal da instituição"""
    try:
        instituicao = get_current_instituicao()
        
        # Parâmetros de data (mês/ano)
        ano = int(request.args.get('ano', datetime.utcnow().year))
        mes = int(request.args.get('mes', datetime.utcnow().month))
        
        # Calcular início e fim do mês
        data_inicio = datetime(ano, mes, 1)
        if mes == 12:
            data_fim = datetime(ano + 1, 1, 1)
        else:
            data_fim = datetime(ano, mes + 1, 1)
        
        # Movimentos do mês
        movimentos_mes = MovimentoStock.query.filter(
            MovimentoStock.instituicao_id == instituicao.id,
            MovimentoStock.data >= data_inicio,
            MovimentoStock.data < data_fim
        ).all()
        
        # Estatísticas do mês
        total_entradas = sum(m.quantidade for m in movimentos_mes if m.tipo_movimento == 'entrada')
        total_saidas = sum(m.quantidade for m in movimentos_mes if m.tipo_movimento == 'saida')
        
        # Beneficiários únicos atendidos no mês
        beneficiarios_mes = set(m.beneficiario_nif for m in movimentos_mes 
                               if m.tipo_movimento == 'saida' and m.beneficiario_nif)
        
        # Itens mais movimentados
        itens_movimentados = {}
        for movimento in movimentos_mes:
            item_nome = movimento.item.nome
            if item_nome not in itens_movimentados:
                itens_movimentados[item_nome] = {'entradas': 0, 'saidas': 0}
            
            if movimento.tipo_movimento == 'entrada':
                itens_movimentados[item_nome]['entradas'] += movimento.quantidade
            else:
                itens_movimentados[item_nome]['saidas'] += movimento.quantidade
        
        # Converter para lista ordenada
        itens_lista = []
        for item_nome, dados in itens_movimentados.items():
            itens_lista.append({
                'item': item_nome,
                'entradas': dados['entradas'],
                'saidas': dados['saidas'],
                'total_movimento': dados['entradas'] + dados['saidas']
            })
        
        itens_lista.sort(key=lambda x: x['total_movimento'], reverse=True)
        
        return jsonify({
            'success': True,
            'relatorio': {
                'periodo': {
                    'ano': ano,
                    'mes': mes,
                    'data_inicio': data_inicio.isoformat(),
                    'data_fim': data_fim.isoformat()
                },
                'estatisticas': {
                    'total_movimentos': len(movimentos_mes),
                    'total_entradas': total_entradas,
                    'total_saidas': total_saidas,
                    'beneficiarios_atendidos': len(beneficiarios_mes)
                },
                'itens_movimentados': itens_lista[:10],  # Top 10
                'movimentos_detalhados': [m.to_dict() for m in movimentos_mes]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@dashboard_bp.route('/alertas', methods=['GET'])
@login_required
def get_alertas():
    """Endpoint para obter alertas e notificações importantes"""
    try:
        alertas = []
        
        # Verificar itens com stock baixo (menos de 10 unidades)
        itens_stock_baixo = []
        itens = ItemStock.query.filter_by(ativo=True).all()
        
        for item in itens:
            stock_total = item.get_stock_total()
            if 0 < stock_total <= 10:
                itens_stock_baixo.append({
                    'item': item.nome,
                    'stock': stock_total,
                    'unidade': item.unidade
                })
        
        if itens_stock_baixo:
            alertas.append({
                'tipo': 'warning',
                'titulo': 'Stock Baixo',
                'mensagem': f'{len(itens_stock_baixo)} itens com stock baixo',
                'detalhes': itens_stock_baixo
            })
        
        # Verificar itens sem stock
        itens_sem_stock = []
        for item in itens:
            stock_total = item.get_stock_total()
            if stock_total <= 0:
                itens_sem_stock.append(item.nome)
        
        if itens_sem_stock:
            alertas.append({
                'tipo': 'danger',
                'titulo': 'Itens Esgotados',
                'mensagem': f'{len(itens_sem_stock)} itens sem stock',
                'detalhes': itens_sem_stock[:5]  # Mostrar apenas os primeiros 5
            })
        
        # Verificar se há beneficiários sem ajuda há muito tempo
        # (Esta funcionalidade pode ser expandida conforme necessário)
        
        return jsonify({
            'success': True,
            'alertas': alertas
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
