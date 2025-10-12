from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Instituicao(db.Model):
    """Modelo para as instituições que utilizam o sistema"""
    __tablename__ = 'instituicoes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20), nullable=True)
    endereco = db.Column(db.Text, nullable=True)
    responsavel = db.Column(db.String(100), nullable=False)
    tipo_instituicao = db.Column(db.String(50), nullable=False)  # ONG, Governo, Religiosa, etc.
    documento_legal = db.Column(db.String(100))  # CNPJ, Registro, etc.
    descricao = db.Column(db.Text)  # Descrição da instituição
    ativa = db.Column(db.Boolean, default=False)  # Inicia inativa, precisa aprovação
    aprovada = db.Column(db.Boolean, default=False)  # Aprovação administrativa
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_aprovacao = db.Column(db.DateTime)
    aprovada_por = db.Column(db.String(100))  # Quem aprovou
    observacoes_admin = db.Column(db.Text)  # Observações administrativas
    
    # Relacionamentos
    movimentos_stock = db.relationship('MovimentoStock', backref='instituicao', lazy=True)
    
    def set_password(self, password):
        """Define a password encriptada para a instituição"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a password está correta"""
        return check_password_hash(self.password_hash, password)
    
    def aprovar(self, aprovada_por_usuario):
        """Aprova a instituição para uso do sistema"""
        self.aprovada = True
        self.ativa = True
        self.data_aprovacao = datetime.utcnow()
        self.aprovada_por = aprovada_por_usuario
    
    def desativar(self, motivo=None):
        """Desativa a instituição"""
        self.ativa = False
        if motivo:
            self.observacoes_admin = f"{self.observacoes_admin or ''}\nDesativada: {motivo}"
    
    def pode_fazer_login(self):
        """Verifica se a instituição pode fazer login"""
        return self.ativa and self.aprovada
    
    def to_dict(self, include_sensitive=False):
        """Converte o objeto para dicionário"""
        data = {
            'id': self.id,
            'nome': self.nome,
            'username': self.username,
            'email': self.email,
            'telefone': self.telefone,
            'endereco': self.endereco,
            'responsavel': self.responsavel,
            'tipo_instituicao': self.tipo_instituicao,
            'documento_legal': self.documento_legal,
            'descricao': self.descricao,
            'ativa': self.ativa,
            'aprovada': self.aprovada,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_aprovacao': self.data_aprovacao.isoformat() if self.data_aprovacao else None
        }
        
        if include_sensitive:
            data.update({
                'aprovada_por': self.aprovada_por,
                'observacoes_admin': self.observacoes_admin
            })
        
        return data
    
    def __repr__(self):
        return f'<Instituicao {self.nome}>'


class Beneficiario(db.Model):
    """Modelo para os beneficiários (vítimas do enchente)"""
    __tablename__ = 'beneficiarios'
    
    nif = db.Column(db.String(20), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer, nullable=True)
    endereco = db.Column(db.Text, nullable=True)
    contacto = db.Column(db.String(20), nullable=True)
    num_agregado = db.Column(db.Integer, nullable=True)
    necessidades = db.Column(db.Text, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    zona_residencia = db.Column(db.String(100), nullable=True)
    perdas_pedidos = db.Column(db.Text, nullable=True)
    data_registo = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    movimentos_stock = db.relationship('MovimentoStock', backref='beneficiario', lazy=True)
    
    def to_dict(self):
        return {
            'nif': self.nif,
            'nome': self.nome,
            'idade': self.idade,
            'endereco': self.endereco,
            'contacto': self.contacto,
            'num_agregado': self.num_agregado,
            'necessidades': self.necessidades,
            'observacoes': self.observacoes,
            'zona_residencia': self.zona_residencia,
            'perdas_pedidos': self.perdas_pedidos,
            'data_registo': self.data_registo.isoformat() if self.data_registo else None
        }
    
    def get_historico_ajuda(self):
        """Retorna o histórico completo de ajuda recebida por este beneficiário"""
        movimentos = MovimentoStock.query.filter_by(
            beneficiario_nif=self.nif,
            tipo_movimento='saida'
        ).order_by(MovimentoStock.data.desc()).all()
        
        return [movimento.to_dict() for movimento in movimentos]
    
    def __repr__(self):
        return f'<Beneficiario {self.nome} ({self.nif})>'


class ItemStock(db.Model):
    """Modelo para os tipos de itens que podem ser doados"""
    __tablename__ = 'itens_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    descricao = db.Column(db.Text, nullable=True)
    unidade = db.Column(db.String(20), nullable=False, default='unidade')  # kg, litro, unidade, etc.
    categoria = db.Column(db.String(50), nullable=True)  # alimentação, vestuário, higiene, etc.
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    movimentos = db.relationship('MovimentoStock', backref='item', lazy=True)
    
    def get_stock_total(self):
        """Calcula o stock total atual deste item (soma de todas as entradas menos saídas)"""
        total_entradas = db.session.query(db.func.sum(MovimentoStock.quantidade)).filter_by(
            item_id=self.id,
            tipo_movimento='entrada'
        ).scalar() or 0
        
        total_saidas = db.session.query(db.func.sum(MovimentoStock.quantidade)).filter_by(
            item_id=self.id,
            tipo_movimento='saida'
        ).scalar() or 0
        
        return total_entradas - total_saidas
    
    def get_stock_por_instituicao(self, instituicao_id):
        """Calcula o stock deste item movimentado por uma instituição específica"""
        total_entradas = db.session.query(db.func.sum(MovimentoStock.quantidade)).filter_by(
            item_id=self.id,
            instituicao_id=instituicao_id,
            tipo_movimento='entrada'
        ).scalar() or 0
        
        total_saidas = db.session.query(db.func.sum(MovimentoStock.quantidade)).filter_by(
            item_id=self.id,
            instituicao_id=instituicao_id,
            tipo_movimento='saida'
        ).scalar() or 0
        
        return total_entradas - total_saidas
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'unidade': self.unidade,
            'categoria': self.categoria,
            'ativo': self.ativo,
            'stock_total': self.get_stock_total(),
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
    
    def __repr__(self):
        return f'<ItemStock {self.nome}>'


class MovimentoStock(db.Model):
    """Modelo para registar todos os movimentos de stock (entradas e saídas)"""
    __tablename__ = 'movimentos_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('itens_stock.id'), nullable=False)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicoes.id'), nullable=False)
    beneficiario_nif = db.Column(db.String(20), db.ForeignKey('beneficiarios.nif'), nullable=True)
    
    tipo_movimento = db.Column(db.String(10), nullable=False)  # 'entrada' ou 'saida'
    quantidade = db.Column(db.Integer, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.Text, nullable=True)
    observacoes = db.Column(db.Text, nullable=True)
    
    # Campos específicos para entradas (doações recebidas)
    origem_doacao = db.Column(db.String(200), nullable=True)  # De onde veio a doação
    
    # Campos específicos para saídas (entregas a beneficiários)
    local_entrega = db.Column(db.String(200), nullable=True)  # Onde foi entregue
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_nome': self.item.nome if self.item else None,
            'item_unidade': self.item.unidade if self.item else None,
            'instituicao_id': self.instituicao_id,
            'instituicao_nome': self.instituicao.nome if self.instituicao else None,
            'beneficiario_nif': self.beneficiario_nif,
            'beneficiario_nome': self.beneficiario.nome if self.beneficiario else None,
            'tipo_movimento': self.tipo_movimento,
            'quantidade': self.quantidade,
            'data': self.data.isoformat() if self.data else None,
            'motivo': self.motivo,
            'observacoes': self.observacoes,
            'origem_doacao': self.origem_doacao,
            'local_entrega': self.local_entrega
        }
    
    def __repr__(self):
        return f'<MovimentoStock {self.tipo_movimento} {self.quantidade} {self.item.nome if self.item else ""}>'


# Função para inicializar dados de exemplo
def init_dados_exemplo():
    """Inicializa o sistema com dados de exemplo"""
    
    # Criar apenas instituição administrativa inicial
    if not Instituicao.query.filter_by(username='caritas').first():
        admin_instituicao = Instituicao(
            nome='Cáritas São Vicente',
            username='caritas',
            email='caritas@saovicente.cv',
            telefone='+238 232 1234',
            endereco='Mindelo, São Vicente',
            responsavel='Administrador do Sistema',
            tipo_instituicao='religiosa',
            descricao='Instituição administrativa do sistema',
            ativa=True,
            aprovada=True  # Pré-aprovada como admin
        )
        admin_instituicao.set_password('sv2024')
        db.session.add(admin_instituicao)
        print("Instituição administrativa criada: caritas / sv2024")
    
    # Criar itens de stock de exemplo
    itens_exemplo = [
        {'nome': 'Arroz 1kg', 'categoria': 'alimentação', 'unidade': 'kg'},
        {'nome': 'Feijão 1kg', 'categoria': 'alimentação', 'unidade': 'kg'},
        {'nome': 'Óleo 1L', 'categoria': 'alimentação', 'unidade': 'litro'},
        {'nome': 'Açúcar 1kg', 'categoria': 'alimentação', 'unidade': 'kg'},
        {'nome': 'Água 1.5L', 'categoria': 'alimentação', 'unidade': 'litro'},
        {'nome': 'Camiseta Adulto', 'categoria': 'vestuário', 'unidade': 'unidade'},
        {'nome': 'Calças Adulto', 'categoria': 'vestuário', 'unidade': 'unidade'},
        {'nome': 'Roupa Criança', 'categoria': 'vestuário', 'unidade': 'unidade'},
        {'nome': 'Sapatos Adulto', 'categoria': 'vestuário', 'unidade': 'par'},
        {'nome': 'Sapatos Criança', 'categoria': 'vestuário', 'unidade': 'par'},
        {'nome': 'Colchão', 'categoria': 'mobiliário', 'unidade': 'unidade'},
        {'nome': 'Cobertor', 'categoria': 'mobiliário', 'unidade': 'unidade'},
        {'nome': 'Lençol', 'categoria': 'mobiliário', 'unidade': 'unidade'},
        {'nome': 'Sabão', 'categoria': 'higiene', 'unidade': 'unidade'},
        {'nome': 'Pasta de Dentes', 'categoria': 'higiene', 'unidade': 'unidade'},
        {'nome': 'Escova de Dentes', 'categoria': 'higiene', 'unidade': 'unidade'},
        {'nome': 'Shampoo', 'categoria': 'higiene', 'unidade': 'unidade'},
        {'nome': 'Fogão Portátil', 'categoria': 'utensílios', 'unidade': 'unidade'},
        {'nome': 'Panela', 'categoria': 'utensílios', 'unidade': 'unidade'},
        {'nome': 'Prato', 'categoria': 'utensílios', 'unidade': 'unidade'}
    ]
    
    for item_data in itens_exemplo:
        if not ItemStock.query.filter_by(nome=item_data['nome']).first():
            item = ItemStock(**item_data)
            db.session.add(item)
    
    db.session.commit()
