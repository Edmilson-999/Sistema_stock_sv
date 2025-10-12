from flask import Blueprint, request, jsonify
from src.models.sistema_models import db, Beneficiario, MovimentoStock
from src.routes.auth import login_required, get_current_instituicao
from sqlalchemy import or_

beneficiarios_bp = Blueprint('beneficiarios', __name__)

@beneficiarios_bp.route('/', methods=['GET'])
@login_required
def get_beneficiarios():
    """Endpoint para obter a lista de beneficiários com pesquisa"""
    try:
        # Parâmetros de pesquisa
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Query base
        query = Beneficiario.query
        
        # Aplicar filtro de pesquisa se fornecido
        if search:
            query = query.filter(
                or_(
                    Beneficiario.nome.ilike(f'%{search}%'),
                    Beneficiario.nif.ilike(f'%{search}%'),
                    Beneficiario.zona_residencia.ilike(f'%{search}%'),
                    Beneficiario.contacto.ilike(f'%{search}%')
                )
            )
        
        # Paginação
        beneficiarios_paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        beneficiarios_list = []
        for beneficiario in beneficiarios_paginated.items:
            beneficiario_dict = beneficiario.to_dict()
            # Adicionar contagem de ajudas recebidas
            total_ajudas = MovimentoStock.query.filter_by(
                beneficiario_nif=beneficiario.nif,
                tipo_movimento='saida'
            ).count()
            beneficiario_dict['total_ajudas'] = total_ajudas
            beneficiarios_list.append(beneficiario_dict)
        
        return jsonify({
            'success': True,
            'beneficiarios': beneficiarios_list,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': beneficiarios_paginated.total,
                'pages': beneficiarios_paginated.pages,
                'has_next': beneficiarios_paginated.has_next,
                'has_prev': beneficiarios_paginated.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@beneficiarios_bp.route('/<nif>', methods=['GET'])
@login_required
def get_beneficiario(nif):
    """Endpoint para obter detalhes de um beneficiário específico"""
    try:
        beneficiario = Beneficiario.query.get(nif)
        
        if not beneficiario:
            return jsonify({'error': 'Beneficiário não encontrado'}), 404
        
        # Obter histórico completo de ajuda
        historico = beneficiario.get_historico_ajuda()
        
        beneficiario_dict = beneficiario.to_dict()
        beneficiario_dict['historico_ajuda'] = historico
        beneficiario_dict['total_ajudas'] = len(historico)
        
        return jsonify({
            'success': True,
            'beneficiario': beneficiario_dict
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@beneficiarios_bp.route('/', methods=['POST'])
@login_required
def create_beneficiario():
    """Endpoint para criar um novo beneficiário"""
    try:
        data = request.get_json()
        
        if not data or 'nif' not in data or 'nome' not in data:
            return jsonify({'error': 'NIF e nome são obrigatórios'}), 400
        
        # Verificar se já existe um beneficiário com este NIF
        if Beneficiario.query.get(data['nif']):
            return jsonify({'error': 'Já existe um beneficiário com este NIF'}), 400
        
        # Criar novo beneficiário
        beneficiario = Beneficiario(
            nif=data['nif'],
            nome=data['nome'],
            idade=data.get('idade'),
            endereco=data.get('endereco'),
            contacto=data.get('contacto'),
            num_agregado=data.get('num_agregado'),
            necessidades=data.get('necessidades'),
            observacoes=data.get('observacoes'),
            zona_residencia=data.get('zona_residencia'),
            perdas_pedidos=data.get('perdas_pedidos')
        )
        
        db.session.add(beneficiario)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Beneficiário criado com sucesso',
            'beneficiario': beneficiario.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@beneficiarios_bp.route('/<nif>', methods=['PUT'])
@login_required
def update_beneficiario(nif):
    """Endpoint para atualizar dados de um beneficiário"""
    try:
        beneficiario = Beneficiario.query.get(nif)
        
        if not beneficiario:
            return jsonify({'error': 'Beneficiário não encontrado'}), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Atualizar campos permitidos
        if 'nome' in data:
            beneficiario.nome = data['nome']
        if 'idade' in data:
            beneficiario.idade = data['idade']
        if 'endereco' in data:
            beneficiario.endereco = data['endereco']
        if 'contacto' in data:
            beneficiario.contacto = data['contacto']
        if 'num_agregado' in data:
            beneficiario.num_agregado = data['num_agregado']
        if 'necessidades' in data:
            beneficiario.necessidades = data['necessidades']
        if 'observacoes' in data:
            beneficiario.observacoes = data['observacoes']
        if 'zona_residencia' in data:
            beneficiario.zona_residencia = data['zona_residencia']
        if 'perdas_pedidos' in data:
            beneficiario.perdas_pedidos = data['perdas_pedidos']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Beneficiário atualizado com sucesso',
            'beneficiario': beneficiario.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@beneficiarios_bp.route('/<nif>/historico', methods=['GET'])
@login_required
def get_historico_beneficiario(nif):
    """Endpoint para obter apenas o histórico de ajuda de um beneficiário"""
    try:
        beneficiario = Beneficiario.query.get(nif)
        
        if not beneficiario:
            return jsonify({'error': 'Beneficiário não encontrado'}), 404
        
        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Query dos movimentos de saída para este beneficiário
        movimentos_query = MovimentoStock.query.filter_by(
            beneficiario_nif=nif,
            tipo_movimento='saida'
        ).order_by(MovimentoStock.data.desc())
        
        movimentos_paginated = movimentos_query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        historico = [movimento.to_dict() for movimento in movimentos_paginated.items]
        
        return jsonify({
            'success': True,
            'historico': historico,
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

@beneficiarios_bp.route('/stats', methods=['GET'])
@login_required
def get_beneficiarios_stats():
    """Endpoint para obter estatísticas dos beneficiários"""
    try:
        total_beneficiarios = Beneficiario.query.count()
        
        # Beneficiários que já receberam ajuda
        beneficiarios_com_ajuda = db.session.query(Beneficiario.nif).join(
            MovimentoStock, Beneficiario.nif == MovimentoStock.beneficiario_nif
        ).filter(MovimentoStock.tipo_movimento == 'saida').distinct().count()
        
        # Beneficiários por zona de residência
        zonas_query = db.session.query(
            Beneficiario.zona_residencia,
            db.func.count(Beneficiario.nif).label('count')
        ).group_by(Beneficiario.zona_residencia).all()
        
        zonas_stats = [{'zona': zona or 'Não especificada', 'count': count} for zona, count in zonas_query]
        
        # Distribuição por faixa etária
        faixas_etarias = [
            {'faixa': '0-17', 'count': Beneficiario.query.filter(Beneficiario.idade.between(0, 17)).count()},
            {'faixa': '18-35', 'count': Beneficiario.query.filter(Beneficiario.idade.between(18, 35)).count()},
            {'faixa': '36-60', 'count': Beneficiario.query.filter(Beneficiario.idade.between(36, 60)).count()},
            {'faixa': '60+', 'count': Beneficiario.query.filter(Beneficiario.idade > 60).count()},
            {'faixa': 'Não informada', 'count': Beneficiario.query.filter(Beneficiario.idade.is_(None)).count()}
        ]
        
        return jsonify({
            'success': True,
            'stats': {
                'total_beneficiarios': total_beneficiarios,
                'beneficiarios_com_ajuda': beneficiarios_com_ajuda,
                'beneficiarios_sem_ajuda': total_beneficiarios - beneficiarios_com_ajuda,
                'zonas_residencia': zonas_stats,
                'faixas_etarias': faixas_etarias
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
