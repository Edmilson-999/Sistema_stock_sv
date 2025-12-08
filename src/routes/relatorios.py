"""
Rotas para gestão de relatórios mensais
"""

from flask import Blueprint, request, jsonify
from src.routes.auth import login_required, get_current_instituicao
from src.services.relatorio_service import RelatorioService
from src.models.sistema_models import db, RelatorioMensal
import json

relatorios_bp = Blueprint('relatorios', __name__)

@relatorios_bp.route('/mensal/gerar', methods=['POST'])
@login_required
def gerar_relatorio_mensal():
    """Gera um relatório mensal para o mês/ano especificado"""
    try:
        instituicao = get_current_instituicao()
        data = request.get_json()
        
        if not data or 'ano' not in data or 'mes' not in data:
            return jsonify({'error': 'Ano e mês são obrigatórios'}), 400
        
        ano = int(data['ano'])
        mes = int(data['mes'])
        
        # Validar mês
        if mes < 1 or mes > 12:
            return jsonify({'error': 'Mês inválido (deve ser entre 1 e 12)'}), 400
        
        # Gerar relatório
        resultado = RelatorioService.gerar_relatorio_mensal(instituicao.id, ano, mes)
        
        if not resultado['sucesso']:
            return jsonify({'error': resultado['erro']}), 500
        
        # Salvar no banco
        salvar = data.get('salvar', True)
        if salvar:
            salvar_result = RelatorioService.salvar_relatorio_mensal(
                instituicao.id, 
                ano, 
                mes, 
                resultado['relatorio'],
                resultado['estatisticas_salvar']
            )
            
            if not salvar_result['sucesso']:
                print(f"⚠️ Não foi possível salvar relatório: {salvar_result['erro']}")
        
        return jsonify({
            'success': True,
            'relatorio': resultado['relatorio'],
            'mensagem': 'Relatório gerado com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@relatorios_bp.route('/mensal/salvar', methods=['POST'])
@login_required
def salvar_relatorio_mensal():
    """Salva um relatório gerado"""
    try:
        instituicao = get_current_instituicao()
        data = request.get_json()
        
        if not data or 'ano' not in data or 'mes' not in data or 'relatorio' not in data:
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Validar e salvar
        resultado = RelatorioService.salvar_relatorio_mensal(
            instituicao.id,
            int(data['ano']),
            int(data['mes']),
            data['relatorio'],
            data.get('estatisticas', {})
        )
        
        if resultado['sucesso']:
            return jsonify({
                'success': True,
                'message': resultado['mensagem']
            }), 200
        else:
            return jsonify({'error': resultado['erro']}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@relatorios_bp.route('/mensal/listar', methods=['GET'])
@login_required
def listar_relatorios():
    """Lista todos os relatórios da instituição"""
    try:
        instituicao = get_current_instituicao()
        
        relatorios = RelatorioService.listar_relatorios_instituicao(instituicao.id)
        
        return jsonify({
            'success': True,
            'relatorios': relatorios
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@relatorios_bp.route('/mensal/<int:relatorio_id>', methods=['GET'])
@login_required
def get_relatorio(relatorio_id):
    """Obtém um relatório específico"""
    try:
        instituicao = get_current_instituicao()
        
        relatorio = RelatorioMensal.query.filter_by(
            id=relatorio_id,
            instituicao_id=instituicao.id
        ).first()
        
        if not relatorio:
            return jsonify({'error': 'Relatório não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'relatorio': relatorio.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@relatorios_bp.route('/mensal/periodos-disponiveis', methods=['GET'])
@login_required
def get_periodos_disponiveis():
    """Retorna os meses/anos para os quais existem dados para gerar relatórios"""
    try:
        instituicao = get_current_instituicao()
        
        periodos = RelatorioService.get_meses_disponiveis(instituicao.id)
        
        return jsonify({
            'success': True,
            'periodos': periodos
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@relatorios_bp.route('/mensal/por-mes/<int:ano>/<int:mes>', methods=['GET'])
@login_required
def get_relatorio_por_mes(ano, mes):
    """Obtém ou gera um relatório para um mês específico"""
    try:
        instituicao = get_current_instituicao()
        
        # Primeiro verificar se já existe salvo
        relatorio_existente = RelatorioMensal.query.filter_by(
            instituicao_id=instituicao.id,
            ano=ano,
            mes=mes
        ).first()
        
        if relatorio_existente:
            return jsonify({
                'success': True,
                'relatorio': relatorio_existente.to_dict(),
                'existe': True
            }), 200
        else:
            # Gerar novo
            resultado = RelatorioService.gerar_relatorio_mensal(instituicao.id, ano, mes)
            
            if resultado['sucesso']:
                return jsonify({
                    'success': True,
                    'relatorio': resultado['relatorio'],
                    'existe': False
                }), 200
            else:
                return jsonify({'error': resultado['erro']}), 500
                
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@relatorios_bp.route('/mensal/<int:relatorio_id>/imprimir', methods=['GET'])
@login_required
def imprimir_relatorio(relatorio_id):
    """Retorna formato otimizado para impressão de relatório"""
    try:
        instituicao = get_current_instituicao()
        
        relatorio = RelatorioMensal.query.filter_by(
            id=relatorio_id,
            instituicao_id=instituicao.id
        ).first()
        
        if not relatorio:
            return jsonify({'error': 'Relatório não encontrado'}), 404
        
        dados = json.loads(relatorio.dados_json)
        
        # Formatar para impressão
        formato_impressao = {
            'cabecalho': {
                'titulo': f'RELATÓRIO MENSAL – {dados["cabecalho"]["mes_nome"]}/{dados["cabecalho"]["ano"]}',
                'instituicao': instituicao.nome,
                'periodo': f'{dados["cabecalho"]["data_inicio"]} a {dados["cabecalho"]["data_fim"]}',
                'data_geracao': dados['cabecalho']['data_geracao']
            },
            
            'resumo': {
                'total_movimentos': dados['resumo']['total_movimentos'],
                'total_entradas': dados['resumo']['total_entradas'],
                'total_saidas': dados['resumo']['total_saidas'],
                'quantidade_total_entradas': dados['resumo']['quantidade_total_entradas'],
                'quantidade_total_saidas': dados['resumo']['quantidade_total_saidas'],
                'saldo_mensal': dados['resumo']['saldo_mensal'],
                'beneficiarios_atendidos': dados['resumo']['beneficiarios_atendidos']
            },
            
            'entradas': {
                'lista': dados['entradas']['lista'],
                'total_itens': len(dados['entradas']['por_item']),
                'itens_principais': list(dados['entradas']['por_item'].items())[:10]
            },
            
            'saidas': {
                'lista': dados['saidas']['lista'],
                'total_itens': len(dados['saidas']['por_item']),
                'itens_principais': list(dados['saidas']['por_item'].items())[:10]
            },
            
            'observacoes': {
                'texto': 'Relatório gerado automaticamente pelo Sistema de Gestão de Stock',
                'recomendacoes': []
            }
        }
        
        return jsonify({
            'success': True,
            'para_impressao': formato_impressao,
            'relatorio_completo': relatorio.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500