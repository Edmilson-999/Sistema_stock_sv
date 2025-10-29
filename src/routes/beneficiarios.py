from flask import Blueprint, request, jsonify
from src.models.sistema_models import db, Beneficiario, MovimentoStock
from src.routes.auth import login_required, get_current_instituicao
from src.services.consulta_service import ConsultaService
from sqlalchemy import or_

beneficiarios_bp = Blueprint('beneficiarios', __name__)

@beneficiarios_bp.route('/consultar_beneficiario', methods=['GET'])
@login_required
def consultar_beneficiario_modal():
    """Endpoint para consultar beneficiário via modal (sem NIF específico)"""
    try:
        nif = request.args.get('nif', '').strip()
        
        if not nif:
            return jsonify({
                'success': False,
                'error': 'NIF é obrigatório para consulta'
            }), 400
        
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

@beneficiarios_bp.route('/consulta_rapida', methods=['GET'])
@login_required
def consulta_rapida():
    """Endpoint para consulta rápida de beneficiários"""
    try:
        search_term = request.args.get('search', '').strip()
        
        if not search_term:
            return jsonify({
                'success': False,
                'error': 'Termo de pesquisa é obrigatório'
            }), 400
        
        instituicao = get_current_instituicao()
        
        # Buscar beneficiários que correspondam ao termo de pesquisa
        beneficiarios = Beneficiario.query.filter(
            Beneficiario.instituicao_registro_id == instituicao.id
        ).filter(
            or_(
                Beneficiario.nome.ilike(f'%{search_term}%'),
                Beneficiario.nif.ilike(f'%{search_term}%'),
                Beneficiario.zona_residencia.ilike(f'%{search_term}%'),
                Beneficiario.contacto.ilike(f'%{search_term}%')
            )
        ).limit(10).all()
        
        resultados = []
        for beneficiario in beneficiarios:
            beneficiario_data = beneficiario.to_dict()
            
            # Adicionar estatísticas rápidas
            total_ajudas = MovimentoStock.query.filter_by(
                beneficiario_nif=beneficiario.nif,
                instituicao_id=instituicao.id,
                tipo_movimento='saida'
            ).count()
            
            beneficiario_data['total_ajudas'] = total_ajudas
            resultados.append(beneficiario_data)
        
        return jsonify({
            'success': True,
            'resultados': resultados,
            'total_encontrado': len(resultados)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500


@beneficiarios_bp.route('/', methods=['GET'])
@login_required
def get_beneficiarios():
    """Endpoint para obter a lista de beneficiários da instituição atual"""
    try:
        instituicao = get_current_instituicao()
        search = request.args.get('search', '').strip()
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Buscar apenas beneficiários registrados pela instituição atual
        query = Beneficiario.query.filter_by(instituicao_registro_id=instituicao.id)
        
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
            # Adicionar contagem de ajudas recebidas (apenas da instituição atual)
            total_ajudas = MovimentoStock.query.filter_by(
                beneficiario_nif=beneficiario.nif,
                instituicao_id=instituicao.id,
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

@beneficiarios_bp.route('/consulta/<nif>', methods=['GET'])
@login_required
def consultar_beneficiario(nif):
    """Endpoint para consultar beneficiário por NIF (consulta cruzada)"""
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

@beneficiarios_bp.route('/<nif>', methods=['GET'])
@login_required
def get_beneficiario(nif):
    """Endpoint para obter detalhes de um beneficiário específico da instituição atual"""
    try:
        instituicao = get_current_instituicao()
        beneficiario = Beneficiario.query.filter_by(
            nif=nif, 
            instituicao_registro_id=instituicao.id
        ).first()
        
        if not beneficiario:
            return jsonify({'error': 'Beneficiário não encontrado'}), 404
        
        # Obter histórico de ajuda apenas da instituição atual
        historico = MovimentoStock.query.filter_by(
            beneficiario_nif=nif,
            instituicao_id=instituicao.id,
            tipo_movimento='saida'
        ).order_by(MovimentoStock.data.desc()).all()
        
        historico_dict = [movimento.to_dict() for movimento in historico]
        
        beneficiario_dict = beneficiario.to_dict()
        beneficiario_dict['historico_ajuda'] = historico_dict
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
    """Endpoint para criar um novo beneficiário associado à instituição atual"""
    try:
        instituicao = get_current_instituicao()
        data = request.get_json()
        
        if not data or 'nif' not in data or 'nome' not in data:
            return jsonify({'error': 'NIF e nome são obrigatórios'}), 400
        
        resultado = ConsultaService.registrar_novo_beneficiario(data, instituicao.id)
        
        if resultado['sucesso']:
            return jsonify({
                'success': True,
                'message': 'Beneficiário criado com sucesso',
                'beneficiario': resultado['beneficiario']
            }), 201
        else:
            return jsonify({'error': resultado['erro']}), 400
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@beneficiarios_bp.route('/<nif>', methods=['PUT'])
@login_required
def update_beneficiario(nif):
    """Endpoint para atualizar dados de um beneficiário da instituição atual"""
    try:
        instituicao = get_current_instituicao()
        beneficiario = Beneficiario.query.filter_by(
            nif=nif,
            instituicao_registro_id=instituicao.id
        ).first()
        
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
    """Endpoint para obter apenas o histórico de ajuda de um beneficiário da instituição atual"""
    try:
        instituicao = get_current_instituicao()
        
        # Verificar se o beneficiário pertence à instituição atual
        beneficiario = Beneficiario.query.filter_by(
            nif=nif,
            instituicao_registro_id=instituicao.id
        ).first()
        
        if not beneficiario:
            return jsonify({'error': 'Beneficiário não encontrado'}), 404
        
        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        # Query dos movimentos de saída para este beneficiário (apenas da instituição atual)
        movimentos_query = MovimentoStock.query.filter_by(
            beneficiario_nif=nif,
            instituicao_id=instituicao.id,
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
    """Endpoint para obter estatísticas dos beneficiários da instituição atual"""
    try:
        instituicao = get_current_instituicao()
        
        # Total de beneficiários da instituição atual
        total_beneficiarios = Beneficiario.query.filter_by(
            instituicao_registro_id=instituicao.id
        ).count()
        
        # Beneficiários que já receberam ajuda da instituição atual
        beneficiarios_com_ajuda = db.session.query(Beneficiario.nif).join(
            MovimentoStock, 
            (Beneficiario.nif == MovimentoStock.beneficiario_nif) &
            (MovimentoStock.instituicao_id == instituicao.id)
        ).filter(
            MovimentoStock.tipo_movimento == 'saida'
        ).distinct().count()
        
        # Beneficiários por zona de residência (apenas da instituição atual)
        zonas_query = db.session.query(
            Beneficiario.zona_residencia,
            db.func.count(Beneficiario.nif).label('count')
        ).filter(
            Beneficiario.instituicao_registro_id == instituicao.id
        ).group_by(Beneficiario.zona_residencia).all()
        
        zonas_stats = [{'zona': zona or 'Não especificada', 'count': count} for zona, count in zonas_query]
        
        # Distribuição por faixa etária (apenas da instituição atual)
        faixas_etarias = [
            {
                'faixa': '0-17', 
                'count': Beneficiario.query.filter(
                    Beneficiario.instituicao_registro_id == instituicao.id,
                    Beneficiario.idade.between(0, 17)
                ).count()
            },
            {
                'faixa': '18-35', 
                'count': Beneficiario.query.filter(
                    Beneficiario.instituicao_registro_id == instituicao.id,
                    Beneficiario.idade.between(18, 35)
                ).count()
            },
            {
                'faixa': '36-60', 
                'count': Beneficiario.query.filter(
                    Beneficiario.instituicao_registro_id == instituicao.id,
                    Beneficiario.idade.between(36, 60)
                ).count()
            },
            {
                'faixa': '60+', 
                'count': Beneficiario.query.filter(
                    Beneficiario.instituicao_registro_id == instituicao.id,
                    Beneficiario.idade > 60
                ).count()
            },
            {
                'faixa': 'Não informada', 
                'count': Beneficiario.query.filter(
                    Beneficiario.instituicao_registro_id == instituicao.id,
                    Beneficiario.idade.is_(None)
                ).count()
            }
        ]
        
        # Estatísticas de ajuda da instituição atual
        total_ajudas_instituicao = MovimentoStock.query.filter_by(
            instituicao_id=instituicao.id,
            tipo_movimento='saida'
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_beneficiarios': total_beneficiarios,
                'beneficiarios_com_ajuda': beneficiarios_com_ajuda,
                'beneficiarios_sem_ajuda': total_beneficiarios - beneficiarios_com_ajuda,
                'total_ajudas_instituicao': total_ajudas_instituicao,
                'zonas_residencia': zonas_stats,
                'faixas_etarias': faixas_etarias
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@beneficiarios_bp.route('/<nif>/historico-completo', methods=['GET'])
@login_required
def get_historico_completo_beneficiario(nif):
    """Endpoint para obter histórico completo do beneficiário (todas as instituições)"""
    try:
        instituicao = get_current_instituicao()
        
        # Consulta cruzada para obter informações completas
        resultado = ConsultaService.consultar_beneficiario_por_nif(nif, instituicao.id)
        
        if not resultado['encontrado']:
            return jsonify({'error': 'Beneficiário não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'consulta': resultado
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500