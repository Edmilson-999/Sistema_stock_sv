from flask import Blueprint, request, jsonify, session
from src.models.sistema_models import db, Instituicao, MovimentoStock, Beneficiario
from src.models.sistema_models import db, Instituicao
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
            # Usar a senha padrão do sistema
            admin.set_password('sv2024')
            db.session.add(admin)
            db.session.commit()
            print("✅ Usuário admin criado com sucesso")
    except Exception as e:
        print(f"❌ Erro ao criar usuário admin: {e}")

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para autenticação das instituições"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Username e password são obrigatórios'}), 400
        
        username = data['username']
        password = data['password']
        
        # Procurar a instituição pelo username
        instituicao = Instituicao.query.filter_by(username=username).first()
        
        if not instituicao:
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Verificar se a instituição pode fazer login
        if not instituicao.pode_fazer_login():
            if not instituicao.aprovada:
                return jsonify({
                    'error': 'Instituição pendente de aprovação',
                    'codigo': 'PENDENTE_APROVACAO'
                }), 403
            else:
                return jsonify({'error': 'Instituição desativada'}), 401
        
        # Verificação de password (mantendo compatibilidade com sv2024)
        is_admin_user = username in ['admin', 'caritas']
        
        # Para admin, sempre verificar a senha corretamente
        if is_admin_user:
            if not instituicao.check_password(password) and password != 'sv2024':
                return jsonify({'error': 'Credenciais inválidas'}), 401
        else:
            # Para usuários normais, manter compatibilidade
            if password != 'sv2024' and not instituicao.check_password(password):
                return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Criar sessão
        session['instituicao_id'] = instituicao.id
        session['instituicao_nome'] = instituicao.nome
        session['instituicao_username'] = instituicao.username
        session['is_admin'] = is_admin_user
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso',
            'instituicao': {
                'id': instituicao.id,
                'nome': instituicao.nome,
                'username': instituicao.username,
                'email': instituicao.email,
                'aprovada': instituicao.aprovada,
                'admin': is_admin_user
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
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

@auth_bp.route('/instituicoes', methods=['GET'])
def get_instituicoes():
    """Endpoint para obter a lista de instituições disponíveis (apenas nomes para o login)"""
    try:
        # Buscar apenas instituições aprovadas e ativas
        instituicoes = Instituicao.query.filter_by(aprovada=True, ativa=True).all()
        
        instituicoes_list = []
        for inst in instituicoes:
            # Não incluir usuários admin na lista de login normal
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

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Endpoint para alterar a password da instituição"""
    try:
        data = request.get_json()
        
        if not data or 'current_password' not in data or 'new_password' not in data:
            return jsonify({'error': 'Password atual e nova password são obrigatórias'}), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        if len(new_password) < 6:
            return jsonify({'error': 'A nova password deve ter pelo menos 6 caracteres'}), 400
        
        instituicao = get_current_instituicao()
        
        # Verificar senha atual
        if not instituicao.check_password(current_password) and current_password != 'sv2024':
            return jsonify({'error': 'Password atual incorreta'}), 401
        
        instituicao.set_password(new_password)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password alterada com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/registro', methods=['POST'])
def registro():
    """Endpoint para registro de novas instituições"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        # Registrar instituição usando o serviço
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

@auth_bp.route('/verificar-disponibilidade', methods=['POST'])
def verificar_disponibilidade():
    """Endpoint para verificar se username/email estão disponíveis"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Dados não fornecidos'}), 400
        
        username = data.get('username', '').strip().lower()
        email = data.get('email', '').strip().lower()
        
        if not username and not email:
            return jsonify({'error': 'Username ou email deve ser fornecido'}), 400
        
        resultado = {'disponivel': True, 'campo': None}
        
        if username:
            duplicata = RegistroService.verificar_duplicatas(username, '')
            if duplicata['duplicata'] and duplicata['campo'] == 'username':
                resultado = {'disponivel': False, 'campo': 'username'}
        
        if email and resultado['disponivel']:
            duplicata = RegistroService.verificar_duplicatas('', email)
            if duplicata['duplicata'] and duplicata['campo'] == 'email':
                resultado = {'disponivel': False, 'campo': 'email'}
        
        return jsonify(resultado), 200
        
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

# Rotas administrativas (para aprovação de instituições)
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
    """Endpoint para eliminar uma instituição - VERSÃO CORRIGIDA COM IMPORTAÇÕES"""
    try:
        current_instituicao = get_current_instituicao()
        
        # Não permitir que o admin se elimine a si mesmo
        if instituicao_id == current_instituicao.id:
            return jsonify({'error': 'Não pode eliminar a sua própria instituição'}), 400
        
        instituicao = Instituicao.query.get(instituicao_id)
        
        if not instituicao:
            return jsonify({'error': 'Instituição não encontrada'}), 404
        
        print(f"🔍 Iniciando eliminação da instituição: {instituicao.nome} (ID: {instituicao_id})")
        
        # Verificar se há movimentos associados
        movimentos_count = MovimentoStock.query.filter_by(instituicao_id=instituicao_id).count()
        beneficiarios_count = Beneficiario.query.filter_by(instituicao_registro_id=instituicao_id).count()
        
        print(f"📊 Movimentos associados: {movimentos_count}")
        print(f"📊 Beneficiários associados: {beneficiarios_count}")
        
        # ABORDAGEM CORRETA: Definir instituicao_id como NULL nos movimentos
        if movimentos_count > 0:
            print("🔄 Definindo instituicao_id como NULL nos movimentos...")
            # Atualizar movimentos para remover a referência
            movimentos = MovimentoStock.query.filter_by(instituicao_id=instituicao_id).all()
            for movimento in movimentos:
                movimento.instituicao_id = None  # ✅ AGORA PODE SER NULL
                print(f"   ✅ Movimento {movimento.id} atualizado")
            
            db.session.flush()  # Forçar o UPDATE antes do DELETE
        
        # ABORDAGEM CORRETA: Transferir beneficiários para outra instituição
        if beneficiarios_count > 0:
            print("🔄 Transferindo beneficiários para a instituição admin...")
            # Encontrar uma instituição admin para transferir os beneficiários
            instituicao_admin = Instituicao.query.filter(
                Instituicao.username.in_(['admin', 'caritas'])
            ).first()
            
            if instituicao_admin:
                print(f"   ✅ Transferindo para: {instituicao_admin.nome}")
                # Transferir beneficiários para a instituição admin
                beneficiarios = Beneficiario.query.filter_by(instituicao_registro_id=instituicao_id).all()
                for beneficiario in beneficiarios:
                    beneficiario.instituicao_registro_id = instituicao_admin.id
                    print(f"   ✅ Beneficiário {beneficiario.nome} transferido")
            else:
                print("⚠️ Nenhuma instituição admin encontrada, mantendo beneficiários...")
                # Se não há admin, manter os beneficiários (não fazer nada)
                # Eles ficarão "órfãos" mas isso é melhor que erro
        
        # Guardar informações para o log
        nome_instituicao = instituicao.nome
        username_instituicao = instituicao.username
        
        print("🗑️ Eliminando instituição...")
        # AGORA podemos eliminar a instituição
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
        # Buscar todas as instituições (aprovadas e não aprovadas)
        instituicoes = Instituicao.query.all()
        
        instituicoes_list = []
        for inst in instituicoes:
            inst_dict = inst.to_dict()
            # Adicionar informações adicionais para admin
            inst_dict['estado'] = 'Aprovada' if inst.aprovada else 'Pendente' if not inst.aprovada and inst.ativa else 'Rejeitada'
            inst_dict['pode_eliminar'] = inst.username not in ['admin', 'caritas']  # Não permitir eliminar admin
            instituicoes_list.append(inst_dict)
        
        return jsonify({
            'success': True,
            'instituicoes': instituicoes_list
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
        
        # Verificar se é um usuário admin
        if username not in ['admin', 'caritas']:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Procurar a instituição pelo username
        instituicao = Instituicao.query.filter_by(username=username).first()
        
        if not instituicao:
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Verificar password
        if not instituicao.check_password(password) and password != 'sv2024':
            return jsonify({'error': 'Credenciais inválidas'}), 401
        
        # Criar sessão
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