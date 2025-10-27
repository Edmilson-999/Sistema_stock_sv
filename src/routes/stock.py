from flask import Blueprint, request, jsonify
from src.models.sistema_models import db, ItemStock, MovimentoStock, Beneficiario
from src.routes.auth import login_required, get_current_instituicao
from src.services.consulta_service import ConsultaService
from sqlalchemy import and_, or_
from datetime import datetime, timedelta

stock_bp = Blueprint('stock', __name__)

@stock_bp.route('/itens', methods=['GET'])
@login_required
def get_itens_stock():
    """Endpoint para obter a lista de itens de stock"""
    try:
        search = request.args.get('search', '').strip()
        categoria = request.args.get('categoria', '').strip()
        
        query = ItemStock.query.filter_by(ativo=True)
        
        # Aplicar filtros
        if search:
            query = query.filter(
                or_(
                    ItemStock.nome.ilike(f'%{search}%'),
                    ItemStock.descricao.ilike(f'%{search}%')
                )
            )
        
        if categoria:
            query = query.filter(ItemStock.categoria == categoria)
        
        itens = query.order_by(ItemStock.categoria, ItemStock.nome).all()
        
        itens_list = []
        instituicao = get_current_instituicao()
        
        for item in itens:
            item_dict = item.to_dict()
            # Adicionar stock movimentado por esta instituição
            item_dict['stock_instituicao'] = item.get_stock_por_instituicao(instituicao.id)
            itens_list.append(item_dict)
        
        return jsonify({
            'success': True,
            'itens': itens_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@stock_bp.route('/itens', methods=['POST'])
@login_required
def create_item_stock():
    """Endpoint para criar um novo item de stock"""
    try:
        data = request.get_json()
        
        if not data or 'nome' not in data:
            return jsonify({'error': 'Nome do item é obrigatório'}), 400
        
        # Verificar se já existe um item com este nome
        if ItemStock.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Já existe um item com este nome'}), 400
        
        item = ItemStock(
            nome=data['nome'],
            descricao=data.get('descricao'),
            unidade=data.get('unidade', 'unidade'),
            categoria=data.get('categoria')
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item criado com sucesso',
            'item': item.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@stock_bp.route('/categorias', methods=['GET'])
@login_required
def get_categorias():
    """Endpoint para obter as categorias de itens disponíveis"""
    try:
        categorias_query = db.session.query(ItemStock.categoria).filter(
            ItemStock.categoria.isnot(None),
            ItemStock.ativo == True
        ).distinct().all()
        
        categorias = [cat[0] for cat in categorias_query if cat[0]]
        categorias.sort()
        
        return jsonify({
            'success': True,
            'categorias': categorias
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@stock_bp.route('/movimentos', methods=['GET'])
@login_required
def get_movimentos():
    """Endpoint para obter os movimentos de stock da instituição atual"""
    try:
        instituicao = get_current_instituicao()
        
        # Parâmetros de filtro
        tipo_movimento = request.args.get('tipo', '')  # 'entrada' ou 'saida'
        item_id = request.args.get('item_id', '')
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Query base - apenas movimentos desta instituição
        query = MovimentoStock.query.filter_by(instituicao_id=instituicao.id)
        
        # Aplicar filtros
        if tipo_movimento:
            query = query.filter(MovimentoStock.tipo_movimento == tipo_movimento)
        
        if item_id:
            query = query.filter(MovimentoStock.item_id == int(item_id))
        
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%Y-%m-%d')
            query = query.filter(MovimentoStock.data >= data_inicio_dt)
        
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(MovimentoStock.data < data_fim_dt)
        
        # Ordenar por data (mais recentes primeiro)
        query = query.order_by(MovimentoStock.data.desc())
        
        # Paginação
        movimentos_paginated = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        movimentos_list = [movimento.to_dict() for movimento in movimentos_paginated.items]
        
        return jsonify({
            'success': True,
            'movimentos': movimentos_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': movimentos_paginated.total,
                'pages': movimentos_paginated.pages,
                'has_next': movimentos_paginated.has_next,
                'has_prev': movimentos_paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@stock_bp.route('/entrada', methods=['POST'])
@login_required
def registar_entrada():
    """Endpoint para registar entrada de stock (doação recebida)"""
    try:
        data = request.get_json()
        
        if not data or 'item_id' not in data or 'quantidade' not in data:
            return jsonify({'error': 'Item e quantidade são obrigatórios'}), 400
        
        item_id = data['item_id']
        quantidade = data['quantidade']
        
        if quantidade <= 0:
            return jsonify({'error': 'Quantidade deve ser maior que zero'}), 400
        
        # Verificar se o item existe
        item = ItemStock.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        instituicao = get_current_instituicao()
        
        # Criar movimento de entrada
        movimento = MovimentoStock(
            item_id=item_id,
            instituicao_id=instituicao.id,
            tipo_movimento='entrada',
            quantidade=quantidade,
            motivo=data.get('motivo', ''),
            observacoes=data.get('observacoes', ''),
            origem_doacao=data.get('origem_doacao', '')
        )
        
        db.session.add(movimento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Entrada registada com sucesso',
            'movimento': movimento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@stock_bp.route('/saida', methods=['POST'])
@login_required
def registar_saida():
    """Endpoint para registar saída de stock (entrega a beneficiário) com sistema de alertas e consulta cruzada"""
    try:
        data = request.get_json()
        
        required_fields = ['item_id', 'quantidade', 'beneficiario_nif']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} é obrigatório'}), 400
        
        item_id = data['item_id']
        quantidade = data['quantidade']
        beneficiario_nif = data['beneficiario_nif']
        forcar_distribuicao = data.get('forcar_distribuicao', False)  # Para ignorar alertas
        
        if quantidade <= 0:
            return jsonify({'error': 'Quantidade deve ser maior que zero'}), 400
        
        # Verificar se o item existe
        item = ItemStock.query.get(item_id)
        if not item:
            return jsonify({'error': 'Item não encontrado'}), 404
        
        # CONSULTA CRUZADA: Verificar beneficiário no sistema completo
        instituicao = get_current_instituicao()
        
        consulta = ConsultaService.consultar_beneficiario_por_nif(
            beneficiario_nif, instituicao.id
        )
        
        if not consulta['encontrado']:
            return jsonify({
                'error': 'Beneficiário não encontrado no sistema. Registre-o primeiro.'
            }), 404
        
        # Verificar se há stock suficiente (stock total, não apenas da instituição)
        stock_total = item.get_stock_total()
        if stock_total < quantidade:
            return jsonify({
                'error': f'Stock insuficiente. Disponível: {stock_total} {item.unidade}'
            }), 400
        
        # SISTEMA DE ALERTAS - Verificar antes da distribuição
        from src.models.alertas_sistema import AlertasSistema
        
        verificacao = AlertasSistema.verificar_antes_distribuicao(
            beneficiario_nif, item_id, quantidade
        )
        
        # Adicionar alertas da consulta cruzada aos alertas do sistema
        if consulta['avisos']:
            if 'alertas' not in verificacao:
                verificacao['alertas'] = []
            verificacao['alertas'].extend(consulta['avisos'])
        
        # Se há alertas e não foi forçada a distribuição, retornar alertas
        if verificacao.get('alertas') and not forcar_distribuicao:
            # Informações da consulta cruzada para o frontend
            info_consulta = {
                'beneficiario': consulta['beneficiario'],
                'total_ajudas_geral': consulta['total_ajudas_instituicao_atual'] + consulta['total_ajudas_outras_instituicoes'],
                'instituicoes_que_ajudaram': consulta['instituicoes_que_ajudaram'],
                'total_ajudas_outras_instituicoes': consulta['total_ajudas_outras_instituicoes']
            }
            
            return jsonify({
                'requer_confirmacao': True,
                'alertas': verificacao['alertas'],
                'sugestoes': verificacao.get('sugestoes', []),
                'beneficiario': {
                    'nome': consulta['beneficiario']['nome'],
                    'nif': consulta['beneficiario']['nif'],
                    'zona': consulta['beneficiario'].get('zona_residencia', '')
                },
                'item': {
                    'nome': item.nome,
                    'unidade': item.unidade
                },
                'quantidade_solicitada': quantidade,
                'info_consulta': info_consulta,
                'message': 'Confirme se deseja prosseguir com a distribuição apesar dos alertas.'
            }), 200
        
        # Criar movimento de saída
        movimento = MovimentoStock(
            item_id=item_id,
            instituicao_id=instituicao.id,
            beneficiario_nif=beneficiario_nif,
            tipo_movimento='saida',
            quantidade=quantidade,
            motivo=data.get('motivo', ''),
            observacoes=data.get('observacoes', ''),
            local_entrega=data.get('local_entrega', '')
        )
        
        db.session.add(movimento)
        db.session.commit()
        
        # Preparar resposta com informações adicionais
        resposta = {
            'success': True,
            'message': 'Saída registada com sucesso',
            'movimento': movimento.to_dict(),
            'info_consulta': {
                'beneficiario': consulta['beneficiario'],
                'total_ajudas_geral': consulta['total_ajudas_instituicao_atual'] + consulta['total_ajudas_outras_instituicoes'],
                'instituicoes_que_ajudaram': consulta['instituicoes_que_ajudaram']
            }
        }
        
        # Adicionar alertas informativos se existirem (mesmo após distribuição)
        if verificacao.get('alertas'):
            resposta['alertas_informativos'] = verificacao['alertas']
        
        if verificacao.get('sugestoes'):
            resposta['sugestoes'] = verificacao['sugestoes']
        
        return jsonify(resposta), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@stock_bp.route('/resumo', methods=['GET'])
@login_required
def get_resumo_stock():
    """Endpoint para obter resumo do stock da instituição"""
    try:
        instituicao = get_current_instituicao()
        
        # Obter todos os itens ativos
        itens = ItemStock.query.filter_by(ativo=True).all()
        
        resumo_itens = []
        total_entradas_instituicao = 0
        total_saidas_instituicao = 0
        
        for item in itens:
            stock_total = item.get_stock_total()
            stock_instituicao = item.get_stock_por_instituicao(instituicao.id)
            
            # Calcular entradas e saídas desta instituição
            entradas = db.session.query(db.func.sum(MovimentoStock.quantidade)).filter_by(
                item_id=item.id,
                instituicao_id=instituicao.id,
                tipo_movimento='entrada'
            ).scalar() or 0
            
            saidas = db.session.query(db.func.sum(MovimentoStock.quantidade)).filter_by(
                item_id=item.id,
                instituicao_id=instituicao.id,
                tipo_movimento='saida'
            ).scalar() or 0
            
            total_entradas_instituicao += entradas
            total_saidas_instituicao += saidas
            
            if stock_total > 0 or stock_instituicao != 0:  # Mostrar apenas itens com movimento
                resumo_itens.append({
                    'item': item.to_dict(),
                    'stock_total': stock_total,
                    'stock_instituicao': stock_instituicao,
                    'entradas_instituicao': entradas,
                    'saidas_instituicao': saidas
                })
        
        # Estatísticas gerais da instituição
        total_movimentos = MovimentoStock.query.filter_by(instituicao_id=instituicao.id).count()
        
        # Movimentos recentes (últimos 7 dias)
        data_limite = datetime.utcnow() - timedelta(days=7)
        movimentos_recentes = MovimentoStock.query.filter(
            MovimentoStock.instituicao_id == instituicao.id,
            MovimentoStock.data >= data_limite
        ).count()
        
        # Beneficiários únicos atendidos por esta instituição
        beneficiarios_unicos = db.session.query(MovimentoStock.beneficiario_nif).filter_by(
            instituicao_id=instituicao.id,
            tipo_movimento='saida'
        ).distinct().count()
        
        return jsonify({
            'success': True,
            'resumo': {
                'itens': resumo_itens,
                'estatisticas': {
                    'total_entradas': total_entradas_instituicao,
                    'total_saidas': total_saidas_instituicao,
                    'total_movimentos': total_movimentos,
                    'movimentos_recentes': movimentos_recentes,
                    'beneficiarios_unicos_atendidos': beneficiarios_unicos
                }
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@stock_bp.route('/movimento/<int:movimento_id>', methods=['GET'])
@login_required
def get_movimento(movimento_id):
    """Endpoint para obter detalhes de um movimento específico"""
    try:
        instituicao = get_current_instituicao()
        
        # Apenas movimentos desta instituição
        movimento = MovimentoStock.query.filter_by(
            id=movimento_id,
            instituicao_id=instituicao.id
        ).first()
        
        if not movimento:
            return jsonify({'error': 'Movimento não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'movimento': movimento.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@stock_bp.route('/movimento/<int:movimento_id>', methods=['PUT'])
@login_required
def update_movimento(movimento_id):
    """Endpoint para atualizar um movimento (apenas observações e motivo)"""
    try:
        instituicao = get_current_instituicao()
        
        movimento = MovimentoStock.query.filter_by(
            id=movimento_id,
            instituicao_id=instituicao.id
        ).first()
        
        if not movimento:
            return jsonify({'error': 'Movimento não encontrado'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Permitir apenas atualização de campos específicos
        if 'motivo' in data:
            movimento.motivo = data['motivo']
        if 'observacoes' in data:
            movimento.observacoes = data['observacoes']
        if 'origem_doacao' in data and movimento.tipo_movimento == 'entrada':
            movimento.origem_doacao = data['origem_doacao']
        if 'local_entrega' in data and movimento.tipo_movimento == 'saida':
            movimento.local_entrega = data['local_entrega']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Movimento atualizado com sucesso',
            'movimento': movimento.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@stock_bp.route('/consulta-rapida/<nif>', methods=['GET'])
@login_required
def consulta_rapida_beneficiario(nif):
    """Endpoint para consulta rápida de beneficiário antes da distribuição"""
    try:
        instituicao = get_current_instituicao()
        
        resultado = ConsultaService.consultar_beneficiario_por_nif(nif, instituicao.id)
        
        if resultado['encontrado']:
            return jsonify({
                'success': True,
                'consulta': resultado
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': resultado.get('mensagem', resultado.get('erro', 'Beneficiário não encontrado'))
            }), 404
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@stock_bp.route('/estatisticas-distribuicao', methods=['GET'])
@login_required
def get_estatisticas_distribuicao():
    """Endpoint para obter estatísticas de distribuição da instituição"""
    try:
        instituicao = get_current_instituicao()
        
        # Total de distribuições (saídas)
        total_distribuicoes = MovimentoStock.query.filter_by(
            instituicao_id=instituicao.id,
            tipo_movimento='saida'
        ).count()
        
        # Distribuições por categoria
        distribuicoes_por_categoria = db.session.query(
            ItemStock.categoria,
            db.func.sum(MovimentoStock.quantidade).label('quantidade_total'),
            db.func.count(MovimentoStock.id).label('total_distribuicoes')
        ).join(
            MovimentoStock, ItemStock.id == MovimentoStock.item_id
        ).filter(
            MovimentoStock.instituicao_id == instituicao.id,
            MovimentoStock.tipo_movimento == 'saida'
        ).group_by(ItemStock.categoria).all()
        
        # Top 5 beneficiários mais ajudados
        top_beneficiarios = db.session.query(
            Beneficiario.nome,
            Beneficiario.nif,
            db.func.count(MovimentoStock.id).label('total_ajudas')
        ).join(
            MovimentoStock, Beneficiario.nif == MovimentoStock.beneficiario_nif
        ).filter(
            MovimentoStock.instituicao_id == instituicao.id,
            MovimentoStock.tipo_movimento == 'saida'
        ).group_by(Beneficiario.nif, Beneficiario.nome
        ).order_by(db.func.count(MovimentoStock.id).desc()
        ).limit(5).all()
        
        # Distribuição por período (últimos 30 dias)
        data_limite = datetime.utcnow() - timedelta(days=30)
        distribuicoes_recentes = MovimentoStock.query.filter(
            MovimentoStock.instituicao_id == instituicao.id,
            MovimentoStock.tipo_movimento == 'saida',
            MovimentoStock.data >= data_limite
        ).count()
        
        return jsonify({
            'success': True,
            'estatisticas': {
                'total_distribuicoes': total_distribuicoes,
                'distribuicoes_recentes_30_dias': distribuicoes_recentes,
                'distribuicoes_por_categoria': [
                    {
                        'categoria': cat.categoria or 'Outros',
                        'quantidade_total': float(cat.quantidade_total or 0),
                        'total_distribuicoes': cat.total_distribuicoes
                    }
                    for cat in distribuicoes_por_categoria
                ],
                'top_beneficiarios': [
                    {
                        'nome': ben.nome,
                        'nif': ben.nif,
                        'total_ajudas': ben.total_ajudas
                    }
                    for ben in top_beneficiarios
                ]
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500