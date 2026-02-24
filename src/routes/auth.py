from flask import Blueprint, request, jsonify, session
from src.models.sistema_models import db, Instituicao, MovimentoStock, Beneficiario
from src.services.registro_service import RegistroService
from functools import wraps

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    """Decorator para verificar se o utilizador está autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'instituicao_id' not in session:
            return jsonify({'error': 'Autenticação necessária'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator para verificar se o usuário é administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'instituicao_id' not in session:
            return jsonify({'error': 'Autenticação necessária'}), 401
        
        instituicao = get_current_instituicao()
        if not instituicao or not instituicao.aprovada or instituicao.username not in ['admin', 'caritas']:
            return jsonify({'error': 'Acesso negado - Permissões de administrador necessárias'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_instituicao():
    """Retorna a instituição atualmente logada"""
    if 'instituicao_id' not in session:
        return None
    return Instituicao.query.get(session['instituicao_id'])

@auth_bp.before_app_request
def create_admin_user():
    """Cria usuário admin se não existir"""
    try:
        admin = Instituicao.query.filter_by(username='admin').first()
        if not admin:
            admin = Instituicao(
                nome='Administrador do Sistema',
                username='admin',
                email='admin@sistema.com',
                tipo_instituicao='governo',
                responsavel='Administrador',
                aprovada=True,
                ativa=True
            )
            admin.set_password('Admin@2024')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")

# ==================== ROTAS PÚBLICAS ====================

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para autenticação das instituições"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        
        username = data['username']
        password = data['password']
        
        instituicao = Instituicao.query.filter_by(username=username).first()
        
        if not instituicao:
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not instituicao.pode_fazer_login():
            if not instituicao.aprovada:
                return jsonify({
                    'error': 'Instituição pendente de aprovação',
                    'codigo': 'PENDENTE_APROVACAO'
                }), 403
            else:
                return jsonify({'error': 'Instituição desativada'}), 401
        
        if not instituicao.check_password(password):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        session['instituicao_id'] = instituicao.id
        session['instituicao_nome'] = instituicao.nome
        session['instituicao_username'] = instituicao.username
        session['is_admin'] = instituicao.username in ['admin', 'caritas']
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',
            'instituicao': {
                'id': instituicao.id,
                'nome': instituicao.nome,
                'username': instituicao.username,
                'email': instituicao.email,
                'aprovada': instituicao.aprovada,
                'admin': instituicao.username in ['admin', 'caritas']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/registro', methods=['POST'])
def registro():
    """Endpoint para registro de novas instituições"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        resultado = RegistroService.registrar_instituicao(data)
        
        if resultado['sucesso']:
            return jsonify({
                'success': True,
                'message': 'Instituição registada com sucesso! Aguarde aprovação para fazer login.',
                'instituicao': resultado['instituicao'].to_dict()
            }), 201
        else:
            return jsonify({'error': resultado['erro']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/tipos-instituicao', methods=['GET'])
def get_tipos_instituicao():
    """Endpoint para obter tipos de instituição disponíveis"""
    return jsonify({
        'tipos': [
            {'valor': 'ong', 'nome': 'ONG - Organização Não Governamental'},
            {'valor': 'governo', 'nome': 'Órgão Governamental'},
            {'valor': 'religiosa', 'nome': 'Instituição Religiosa'},
            {'valor': 'empresa', 'nome': 'Empresa Privada'},
            {'valor': 'cooperativa', 'nome': 'Cooperativa'},
            {'valor': 'associacao', 'nome': 'Associação'},
            {'valor': 'fundacao', 'nome': 'Fundação'},
            {'valor': 'outro', 'nome': 'Outro'}
        ]
    }), 200

@auth_bp.route('/instituicoes', methods=['GET'])
def get_instituicoes():
    """Endpoint para obter a lista de instituições disponíveis (apenas nomes para o login)"""
    try:
        instituicoes = Instituicao.query.filter_by(aprovada=True, ativa=True).all()
        
        instituicoes_list = []
        for inst in instituicoes:
            if inst.username not in ['admin', 'caritas']:
                instituicoes_list.append({
                    'username': inst.username,
                    'nome': inst.nome
                })
        
        return jsonify({
            'success': True,
            'instituicoes': instituicoes_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Endpoint para verificar se o utilizador está autenticado"""
    try:
        if 'instituicao_id' in session:
            instituicao = get_current_instituicao()
            if instituicao and instituicao.ativa:
                is_admin = instituicao.username in ['admin', 'caritas']
                return jsonify({
                    'authenticated': True,
                    'instituicao': {
                        'id': instituicao.id,
                        'nome': instituicao.nome,
                        'username': instituicao.username,
                        'admin': is_admin
                    }
                }), 200
        
        return jsonify({'authenticated': False}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint para terminar a sessão"""
    try:
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logout realizado com sucesso'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Endpoint para obter informações da instituição logada"""
    try:
        instituicao = get_current_instituicao()
        
        if not instituicao:
            return jsonify({'error': 'Sessão inválida'}), 401
        
        return jsonify({
            'success': True,
            'instituicao': instituicao.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# ==================== ROTAS DE GESTÃO DE PASSWORDS ====================

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_my_password():
    """✅ RENOMEADA: Endpoint para instituição alterar a sua própria password"""
    try:
        data = request.get_json()
        
        if not data or 'current_password' not in data or 'new_password' not in data:
            return jsonify({'error': 'Password atual e nova password são obrigatórias'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        if len(new_password) < 8:
            return jsonify({'error': 'A nova password deve ter pelo menos 8 caracteres'}), 400
        
        if not any(c.isupper() for c in new_password):
            return jsonify({'error': 'A nova password deve conter pelo menos uma letra maiúscula'}), 400
        
        if not any(c.islower() for c in new_password):
            return jsonify({'error': 'A nova password deve conter pelo menos uma letra minúscula'}), 400
        
        if not any(c.isdigit() for c in new_password):
            return jsonify({'error': 'A nova password deve conter pelo menos um número'}), 400
        
        instituicao = get_current_instituicao()
        
        if not instituicao.check_password(current_password):
            return jsonify({'error': 'Password atual incorreta'}), 401
        
        if instituicao.check_password(new_password):
            return jsonify({'error': 'A nova password deve ser diferente da atual'}), 400
        
        instituicao.set_password(new_password)
        instituicao.primeira_password = False  # ✅ Marcar que já não é primeira password
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password alterada com sucesso. Use a nova password no próximo login.'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/admin/change-password', methods=['POST'])
@admin_required
def admin_change_institution_password():
    """✅ RENOMEADA: Endpoint para administrador alterar password de outra instituição"""
    try:
        data = request.get_json()
        
        if not data or 'instituicao_id' not in data or 'new_password' not in data:
            return jsonify({'error': 'ID da instituição e nova password são obrigatórios'}), 400
        
        instituicao_id = data['instituicao_id']
        new_password = data['new_password']
        
        if len(new_password) < 8:
            return jsonify({'error': 'A nova password deve ter pelo menos 8 caracteres'}), 400
        
        instituicao = Instituicao.query.get(instituicao_id)
        
        if not instituicao:
            return jsonify({'error': 'Instituição não encontrada'}), 404
        
        current_admin = get_current_instituicao()
        if instituicao_id == current_admin.id:
            return jsonify({'error': 'Use a opção "Alterar minha password" para alterar sua própria password'}), 400
        
        instituicao.set_password(new_password)
        instituicao.primeira_password = True  # ✅ Marcar como primeira password para forçar troca no próximo login
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Password da instituição {instituicao.nome} alterada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/validate-password', methods=['POST'])
def validate_password_strength():
    """✅ RENOMEADA: Endpoint para validar a força da password"""
    try:
        data = request.get_json()
        
        if not data or 'password' not in data:
            return jsonify({'error': 'Password não fornecida'}), 400
        
        password = data['password']
        feedback = []
        strength = 0
        
        if len(password) >= 8:
            strength += 1
        else:
            feedback.append('Mínimo 8 caracteres')
        
        if any(c.isupper() for c in password):
            strength += 1
        else:
            feedback.append('Pelo menos uma maiúscula')
        
        if any(c.islower() for c in password):
            strength += 1
        else:
            feedback.append('Pelo menos uma minúscula')
        
        if any(c.isdigit() for c in password):
            strength += 1
        else:
            feedback.append('Pelo menos um número')
        
        if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            strength += 1
        else:
            feedback.append('Pelo menos um caractere especial (!@#$%...)')
        
        if strength <= 2:
            level = 'Fraca'
        elif strength <= 3:
            level = 'Média'
        elif strength <= 4:
            level = 'Boa'
        else:
            level = 'Forte'
        
        return jsonify({
            'success': True,
            'strength': strength,
            'level': level,
            'feedback': feedback
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

# ==================== ROTAS ADMINISTRATIVAS ====================

@auth_bp.route('/admin/instituicoes-pendentes', methods=['GET'])
@admin_required
def get_instituicoes_pendentes():
    """Endpoint para listar instituições pendentes de aprovação"""
    try:
        instituicoes = RegistroService.listar_instituicoes_pendentes()
        
        return jsonify({
            'success': True,
            'instituicoes': [inst.to_dict() for inst in instituicoes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/admin/aprovar-instituicao/<int:instituicao_id>', methods=['POST'])
@admin_required
def aprovar_instituicao(instituicao_id):
    """Endpoint para aprovar uma instituição"""
    try:
        current_instituicao = get_current_instituicao()
        resultado = RegistroService.aprovar_instituicao(
            instituicao_id, 
            current_instituicao.nome
        )
        
        if resultado['sucesso']:
            return jsonify({
                'success': True,
                'message': 'Instituição aprovada com sucesso'
            }), 200
        else:
            return jsonify({'error': resultado['erro']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/admin/rejeitar-instituicao/<int:instituicao_id>', methods=['POST'])
@admin_required
def rejeitar_instituicao(instituicao_id):
    """Endpoint para rejeitar uma instituição"""
    try:
        data = request.get_json()
        motivo = data.get('motivo', 'Não especificado')
        
        current_instituicao = get_current_instituicao()
        resultado = RegistroService.rejeitar_instituicao(
            instituicao_id, 
            motivo,
            current_instituicao.nome
        )
        
        if resultado['sucesso']:
            return jsonify({
                'success': True,
                'message': 'Instituição rejeitada'
            }), 200
        else:
            return jsonify({'error': resultado['erro']}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/admin/eliminar-instituicao/<int:instituicao_id>', methods=['DELETE'])
@admin_required
def eliminar_instituicao(instituicao_id):
    """Endpoint para eliminar uma instituição"""
    try:
        current_instituicao = get_current_instituicao()
        
        if instituicao_id == current_instituicao.id:
            return jsonify({'error': 'Não pode eliminar a sua própria instituição'}), 400
        
        instituicao = Instituicao.query.get(instituicao_id)
        
        if not instituicao:
            return jsonify({'error': 'Instituição não encontrada'}), 404
        
        print(f"🔍 Iniciando eliminação da instituição: {instituicao.nome} (ID: {instituicao_id})")
        
        movimentos_count = MovimentoStock.query.filter_by(instituicao_id=instituicao_id).count()
        beneficiarios_count = Beneficiario.query.filter_by(instituicao_registro_id=instituicao_id).count()
        
        print(f"📊 Movimentos associados: {movimentos_count}")
        print(f"📊 Beneficiários associados: {beneficiarios_count}")
        
        if movimentos_count > 0:
            print("🔄 Definindo instituicao_id como NULL nos movimentos...")
            movimentos = MovimentoStock.query.filter_by(instituicao_id=instituicao_id).all()
            for movimento in movimentos:
                movimento.instituicao_id = None
                print(f"   ✅ Movimento {movimento.id} atualizado")
            
            db.session.flush()
        
        if beneficiarios_count > 0:
            print("🔄 Transferindo beneficiários para a instituição admin...")
            instituicao_admin = Instituicao.query.filter(
                Instituicao.username.in_(['admin', 'caritas'])
            ).first()
            
            if instituicao_admin:
                print(f"   ✅ Transferindo para: {instituicao_admin.nome}")
                beneficiarios = Beneficiario.query.filter_by(instituicao_registro_id=instituicao_id).all()
                for beneficiario in beneficiarios:
                    beneficiario.instituicao_registro_id = instituicao_admin.id
                    print(f"   ✅ Beneficiário {beneficiario.nome} transferido")
            else:
                print("⚠️ Nenhuma instituição admin encontrada, mantendo beneficiários...")
        
        nome_instituicao = instituicao.nome
        username_instituicao = instituicao.username
        
        print("🗑️ Eliminando instituição...")
        db.session.delete(instituicao)
        db.session.commit()
        
        print(f"✅ Instituição eliminada por {current_instituicao.nome}: {nome_instituicao} ({username_instituicao})")
        print(f"📊 Estatísticas: {movimentos_count} movimentos atualizados, {beneficiarios_count} beneficiários transferidos")
        
        return jsonify({
            'success': True,
            'message': f'Instituição {nome_instituicao} eliminada com sucesso',
            'stats': {
                'movimentos_afetados': movimentos_count,
                'beneficiarios_transferidos': beneficiarios_count
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Erro detalhado ao eliminar instituição: {str(e)}")
        import traceback
        print(f"🔍 Stack trace: {traceback.format_exc()}")
        return jsonify({'error': f'Erro ao eliminar instituição: {str(e)}'}), 500

@auth_bp.route('/admin/todas-instituicoes', methods=['GET'])
@admin_required
def get_todas_instituicoes():
    """Endpoint para listar todas as instituições (para administração)"""
    try:
        instituicoes = Instituicao.query.all()
        
        instituicoes_list = []
        for inst in instituicoes:
            inst_dict = inst.to_dict()
            inst_dict['estado'] = 'Aprovada' if inst.aprovada else 'Pendente' if not inst.aprovada and inst.ativa else 'Rejeitada'
            inst_dict['pode_eliminar'] = inst.username not in ['admin', 'caritas']
            instituicoes_list.append(inst_dict)
        
        current_admin = get_current_instituicao()
        
        return jsonify({
            'success': True,
            'instituicoes': instituicoes_list,
            'admin': {
                'nome': current_admin.nome,
                'username': current_admin.username
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/admin/estatisticas', methods=['GET'])
@admin_required
def get_estatisticas_admin():
    """Endpoint para obter estatísticas administrativas"""
    try:
        estatisticas = RegistroService.estatisticas_registro()
        
        return jsonify({
            'success': True,
            'estatisticas': estatisticas
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/admin/info', methods=['GET'])
@admin_required
def get_admin_info():
    """Endpoint para obter informações do administrador"""
    try:
        current_instituicao = get_current_instituicao()
        
        return jsonify({
            'success': True,
            'admin': {
                'id': current_instituicao.id,
                'nome': current_instituicao.nome,
                'username': current_instituicao.username,
                'email': current_instituicao.email
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/admin/validate-access', methods=['POST'])
def validate_admin_access():
    """Endpoint para validar acesso administrativo"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        
        username = data['username']
        password = data['password']
        
        if username not in ['admin', 'caritas']:
            return jsonify({'error': 'Acesso negado'}), 403
        
        instituicao = Instituicao.query.filter_by(username=username).first()
        
        if not instituicao:
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        if not instituicao.check_password(password):
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        session['instituicao_id'] = instituicao.id
        session['instituicao_nome'] = instituicao.nome
        session['instituicao_username'] = instituicao.username
        session['is_admin'] = True
        
        return jsonify({
            'success': True,
            'message': 'Acesso administrativo concedido',
            'instituicao': {
                'id': instituicao.id,
                'nome': instituicao.nome,
                'username': instituicao.username,
                'email': instituicao.email,
                'admin': True
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500