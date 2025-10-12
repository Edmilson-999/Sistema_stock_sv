"""
Rotas para o sistema de alertas e controles inteligentes
"""

from flask import Blueprint, request, jsonify
from src.routes.auth import login_required, get_current_instituicao
from src.models.alertas_sistema import AlertasSistema

alertas_bp = Blueprint('alertas', __name__)

@alertas_bp.route('/verificar-distribuicao', methods=['POST'])
@login_required
def verificar_distribuicao():
    """Endpoint para verificar se uma distribuição é apropriada"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['beneficiario_nif', 'item_id', 'quantidade']):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        beneficiario_nif = data['beneficiario_nif']
        item_id = data['item_id']
        quantidade = data['quantidade']
        
        verificacao = AlertasSistema.verificar_antes_distribuicao(
            beneficiario_nif, item_id, quantidade
        )
        
        return jsonify({
            'success': True,
            'verificacao': verificacao
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@alertas_bp.route('/beneficiarios-menos-ajuda', methods=['GET'])
@login_required
def get_beneficiarios_menos_ajuda():
    """Endpoint para obter beneficiários que receberam menos ajuda"""
    try:
        categoria = request.args.get('categoria', None)
        limite = int(request.args.get('limite', 10))
        
        beneficiarios = AlertasSistema.buscar_beneficiarios_menos_ajuda(categoria, limite)
        
        return jsonify({
            'success': True,
            'beneficiarios': beneficiarios,
            'categoria': categoria,
            'total': len(beneficiarios)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@alertas_bp.route('/relatorio-distribuicao', methods=['GET'])
@login_required
def get_relatorio_distribuicao():
    """Endpoint para obter relatório de distribuição equitativa"""
    try:
        relatorio = AlertasSistema.gerar_relatorio_distribuicao_equitativa()
        
        return jsonify({
            'success': True,
            'relatorio': relatorio
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@alertas_bp.route('/configurar-limites', methods=['POST'])
@login_required
def configurar_limites():
    """Endpoint para configurar limites personalizados (apenas para administradores)"""
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['categoria', 'item', 'quantidade_maxima', 'periodo_dias']):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Verificar se a instituição tem permissão (pode ser expandido)
        instituicao = get_current_instituicao()
        if not instituicao:
            return jsonify({'error': 'Instituição não encontrada'}), 401
        
        categoria = data['categoria']
        item = data['item']
        quantidade_maxima = int(data['quantidade_maxima'])
        periodo_dias = int(data['periodo_dias'])
        
        AlertasSistema.configurar_limites_personalizados(
            categoria, item, quantidade_maxima, periodo_dias
        )
        
        return jsonify({
            'success': True,
            'message': f'Limite configurado: {quantidade_maxima} {item} por {periodo_dias} dias na categoria {categoria}'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@alertas_bp.route('/limites-atuais', methods=['GET'])
@login_required
def get_limites_atuais():
    """Endpoint para obter os limites atualmente configurados"""
    try:
        return jsonify({
            'success': True,
            'limites': AlertasSistema.LIMITES_CATEGORIA
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500
