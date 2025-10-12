"""
Serviço para registro e gestão de instituições
Implementa fluxo de registro, validação e aprovação
"""

import re
from datetime import datetime
from src.models.sistema_models import db, Instituicao
from sqlalchemy.exc import IntegrityError

class RegistroService:
    """Serviço para gestão de registro de instituições"""
    
    TIPOS_INSTITUICAO = [
        'ong',
        'governo',
        'religiosa',
        'empresa',
        'cooperativa',
        'associacao',
        'fundacao',
        'outro'
    ]
    
    @staticmethod
    def validar_dados_registro(dados):
        """
        Valida os dados de registro de uma instituição
        
        Args:
            dados (dict): Dados do formulário de registro
            
        Returns:
            dict: {'valido': bool, 'erros': list}
        """
        erros = []
        
        # Campos obrigatórios
        campos_obrigatorios = [
            'nome', 'username', 'password', 'email', 
            'responsavel', 'tipo_instituicao'
        ]
        
        for campo in campos_obrigatorios:
            if not dados.get(campo) or not dados[campo].strip():
                erros.append(f'{campo.replace("_", " ").title()} é obrigatório')
        
        # Validar email
        if dados.get('email'):
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_regex, dados['email']):
                erros.append('Email inválido')
        
        # Validar username
        if dados.get('username'):
            username = dados['username'].strip()
            if len(username) < 3:
                erros.append('Username deve ter pelo menos 3 caracteres')
            if not re.match(r'^[a-zA-Z0-9_]+$', username):
                erros.append('Username deve conter apenas letras, números e underscore')
        
        # Validar password
        if dados.get('password'):
            password = dados['password']
            if len(password) < 6:
                erros.append('Password deve ter pelo menos 6 caracteres')
        
        # Validar tipo de instituição
        if dados.get('tipo_instituicao'):
            if dados['tipo_instituicao'] not in RegistroService.TIPOS_INSTITUICAO:
                erros.append('Tipo de instituição inválido')
        
        # Validar telefone (se fornecido)
        if dados.get('telefone'):
            telefone = dados['telefone'].strip()
            if telefone and not re.match(r'^[\d\s\+\-\(\)]+$', telefone):
                erros.append('Telefone inválido')
        
        return {
            'valido': len(erros) == 0,
            'erros': erros
        }
    
    @staticmethod
    def verificar_duplicatas(username, email):
        """
        Verifica se já existe instituição com mesmo username ou email
        
        Args:
            username (str): Username a verificar
            email (str): Email a verificar
            
        Returns:
            dict: {'duplicata': bool, 'campo': str}
        """
        # Verificar username
        if Instituicao.query.filter_by(username=username).first():
            return {'duplicata': True, 'campo': 'username'}
        
        # Verificar email
        if Instituicao.query.filter_by(email=email).first():
            return {'duplicata': True, 'campo': 'email'}
        
        return {'duplicata': False, 'campo': None}
    
    @staticmethod
    def registrar_instituicao(dados):
        """
        Registra uma nova instituição no sistema
        
        Args:
            dados (dict): Dados validados da instituição
            
        Returns:
            dict: {'sucesso': bool, 'instituicao': Instituicao, 'erro': str}
        """
        try:
            # Validar dados
            validacao = RegistroService.validar_dados_registro(dados)
            if not validacao['valido']:
                return {
                    'sucesso': False,
                    'erro': '; '.join(validacao['erros']),
                    'instituicao': None
                }
            
            # Verificar duplicatas
            duplicata = RegistroService.verificar_duplicatas(
                dados['username'], dados['email']
            )
            if duplicata['duplicata']:
                return {
                    'sucesso': False,
                    'erro': f'{duplicata["campo"].title()} já está em uso',
                    'instituicao': None
                }
            
            # Criar nova instituição
            instituicao = Instituicao(
                nome=dados['nome'].strip(),
                username=dados['username'].strip().lower(),
                email=dados['email'].strip().lower(),
                telefone=dados.get('telefone', '').strip(),
                endereco=dados.get('endereco', '').strip(),
                responsavel=dados['responsavel'].strip(),
                tipo_instituicao=dados['tipo_instituicao'],
                documento_legal=dados.get('documento_legal', '').strip(),
                descricao=dados.get('descricao', '').strip(),
                ativa=False,  # Inicia inativa
                aprovada=False  # Precisa aprovação
            )
            
            # Definir password
            instituicao.set_password(dados['password'])
            
            # Salvar na base de dados
            db.session.add(instituicao)
            db.session.commit()
            
            return {
                'sucesso': True,
                'instituicao': instituicao,
                'erro': None
            }
            
        except IntegrityError as e:
            db.session.rollback()
            return {
                'sucesso': False,
                'erro': 'Dados duplicados (username ou email já existem)',
                'instituicao': None
            }
        except Exception as e:
            db.session.rollback()
            return {
                'sucesso': False,
                'erro': f'Erro interno: {str(e)}',
                'instituicao': None
            }
    
    @staticmethod
    def listar_instituicoes_pendentes():
        """
        Lista instituições pendentes de aprovação
        
        Returns:
            list: Lista de instituições não aprovadas
        """
        return Instituicao.query.filter_by(aprovada=False).order_by(
            Instituicao.data_criacao.desc()
        ).all()
    
    @staticmethod
    def aprovar_instituicao(instituicao_id, aprovada_por):
        """
        Aprova uma instituição para uso do sistema
        
        Args:
            instituicao_id (int): ID da instituição
            aprovada_por (str): Quem está aprovando
            
        Returns:
            dict: {'sucesso': bool, 'erro': str}
        """
        try:
            instituicao = Instituicao.query.get(instituicao_id)
            if not instituicao:
                return {'sucesso': False, 'erro': 'Instituição não encontrada'}
            
            if instituicao.aprovada:
                return {'sucesso': False, 'erro': 'Instituição já está aprovada'}
            
            instituicao.aprovar(aprovada_por)
            db.session.commit()
            
            return {'sucesso': True, 'erro': None}
            
        except Exception as e:
            db.session.rollback()
            return {'sucesso': False, 'erro': f'Erro interno: {str(e)}'}
    
    @staticmethod
    def rejeitar_instituicao(instituicao_id, motivo, rejeitada_por):
        """
        Rejeita uma instituição
        
        Args:
            instituicao_id (int): ID da instituição
            motivo (str): Motivo da rejeição
            rejeitada_por (str): Quem está rejeitando
            
        Returns:
            dict: {'sucesso': bool, 'erro': str}
        """
        try:
            instituicao = Instituicao.query.get(instituicao_id)
            if not instituicao:
                return {'sucesso': False, 'erro': 'Instituição não encontrada'}
            
            # Adicionar observação de rejeição
            observacao = f"Rejeitada por {rejeitada_por} em {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}: {motivo}"
            instituicao.observacoes_admin = f"{instituicao.observacoes_admin or ''}\n{observacao}"
            
            # Remover da base de dados ou marcar como rejeitada
            db.session.delete(instituicao)
            db.session.commit()
            
            return {'sucesso': True, 'erro': None}
            
        except Exception as e:
            db.session.rollback()
            return {'sucesso': False, 'erro': f'Erro interno: {str(e)}'}
    
    @staticmethod
    def buscar_instituicao_por_username(username):
        """
        Busca instituição por username
        
        Args:
            username (str): Username da instituição
            
        Returns:
            Instituicao: Objeto da instituição ou None
        """
        return Instituicao.query.filter_by(username=username.lower()).first()
    
    @staticmethod
    def estatisticas_registro():
        """
        Retorna estatísticas de registro de instituições
        
        Returns:
            dict: Estatísticas do sistema
        """
        total = Instituicao.query.count()
        aprovadas = Instituicao.query.filter_by(aprovada=True).count()
        pendentes = Instituicao.query.filter_by(aprovada=False).count()
        ativas = Instituicao.query.filter_by(ativa=True).count()
        
        return {
            'total_instituicoes': total,
            'aprovadas': aprovadas,
            'pendentes': pendentes,
            'ativas': ativas,
            'taxa_aprovacao': round((aprovadas / total * 100) if total > 0 else 0, 1)
        }
