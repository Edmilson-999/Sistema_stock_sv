from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Instituicao(db.Model):
    __tablename__ = 'instituicoes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    responsavel = db.Column(db.String(100), nullable=False)
    tipo_instituicao = db.Column(db.String(50), nullable=False)
    documento_legal = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    password_hash = db.Column(db.String(256))
    aprovada = db.Column(db.Boolean, default=False)
    ativa = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_aprovacao = db.Column(db.DateTime)
    aprovada_por = db.Column(db.String(100))
    observacoes_admin = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def pode_fazer_login(self):
        return self.ativa and self.aprovada

    def aprovar(self, aprovada_por):
        self.aprovada = True
        self.data_aprovacao = datetime.utcnow()
        self.aprovada_por = aprovada_por

    def to_dict(self):
        return {
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
            'aprovada': self.aprovada,
            'ativa': self.ativa,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'data_aprovacao': self.data_aprovacao.isoformat() if self.data_aprovacao else None
        }

class Beneficiario(db.Model):
    __tablename__ = 'beneficiarios'
    
    nif = db.Column(db.String(20), primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    idade = db.Column(db.Integer)
    endereco = db.Column(db.Text)
    contacto = db.Column(db.String(20))
    num_agregado = db.Column(db.Integer)
    necessidades = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    zona_residencia = db.Column(db.String(50))
    perdas_pedidos = db.Column(db.Text)
    instituicao_registro_id = db.Column(db.Integer, db.ForeignKey('instituicoes.id'))
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    instituicao_registro = db.relationship('Instituicao', backref='beneficiarios_registrados')
    
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
            'instituicao_registro_id': self.instituicao_registro_id,
            'data_registro': self.data_registro.isoformat() if self.data_registro else None
        }
    
    def get_historico_ajuda(self):
        """Retorna o histórico de ajuda deste beneficiário"""
        movimentos = MovimentoStock.query.filter_by(
            beneficiario_nif=self.nif,
            tipo_movimento='saida'
        ).order_by(MovimentoStock.data.desc()).all()
        
        historico = []
        for movimento in movimentos:
            historico.append({
                'id': movimento.id,
                'data': movimento.data.isoformat(),
                'item_nome': movimento.item.nome,
                'quantidade': movimento.quantidade,
                'item_unidade': movimento.item.unidade,
                'instituicao_nome': movimento.instituicao_movimento.nome,
                'motivo': movimento.motivo
            })
        
        return historico

class ItemStock(db.Model):
    __tablename__ = 'itens_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    descricao = db.Column(db.Text)
    unidade = db.Column(db.String(20), default='unidade')
    categoria = db.Column(db.String(50))
    ativo = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'unidade': self.unidade,
            'categoria': self.categoria,
            'ativo': self.ativo,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }
    
    def get_stock_total(self):
        """Calcula o stock total deste item"""
        entradas = db.session.query(db.func.sum(MovimentoStock.quantidade)).filter_by(
            item_id=self.id, tipo_movimento='entrada'
        ).scalar() or 0
        
        saidas = db.session.query(db.func.sum(MovimentoStock.quantidade)).filter_by(
            item_id=self.id, tipo_movimento='saida'
        ).scalar() or 0
        
        return entradas - saidas
    
    def get_stock_por_instituicao(self, instituicao_id):
        """Calcula o stock deste item para uma instituição específica"""
        entradas = db.session.query(db.func.sum(MovimentoStock.quantidade)).filter_by(
            item_id=self.id, instituicao_id=instituicao_id, tipo_movimento='entrada'
        ).scalar() or 0
        
        saidas = db.session.query(db.func.sum(MovimentoStock.quantidade)).filter_by(
            item_id=self.id, instituicao_id=instituicao_id, tipo_movimento='saida'
        ).scalar() or 0
        
        return entradas - saidas

class MovimentoStock(db.Model):
    __tablename__ = 'movimentos_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('itens_stock.id'), nullable=False)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicoes.id'), nullable=True)
    beneficiario_nif = db.Column(db.String(20), db.ForeignKey('beneficiarios.nif'))
    tipo_movimento = db.Column(db.Enum('entrada', 'saida'), nullable=False)
    quantidade = db.Column(db.Float, nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    motivo = db.Column(db.Text)
    observacoes = db.Column(db.Text)
    origem_doacao = db.Column(db.String(100))  # Para entradas
    local_entrega = db.Column(db.String(100))  # Para saídas
    
    # Relacionamentos CORRIGIDOS (nomes únicos)
    item = db.relationship('ItemStock', backref='movimentos_stock')
    instituicao_movimento = db.relationship('Instituicao', backref='movimentos_stock')  
    beneficiario = db.relationship('Beneficiario', backref='movimentos_stock') 
    
    def to_dict(self):
        return {
            'id': self.id,
            'item_id': self.item_id,
            'item_nome': self.item.nome if self.item else None,
            'item_unidade': self.item.unidade if self.item else None,
            'instituicao_id': self.instituicao_id,
            'instituicao_nome': self.instituicao_movimento.nome if self.instituicao_movimento else None,
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

class RelatorioMensal(db.Model):
    __tablename__ = 'relatorios_mensais'
    
    id = db.Column(db.Integer, primary_key=True)
    instituicao_id = db.Column(db.Integer, db.ForeignKey('instituicoes.id'), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)  # 1-12
    data_geracao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Dados do relatório (armazenados como JSON)
    dados_json = db.Column(db.Text, nullable=False)
    
    # Metadados
    total_entradas = db.Column(db.Integer, default=0)
    total_saidas = db.Column(db.Integer, default=0)
    saldo_mensal = db.Column(db.Integer, default=0)
    movimentos_count = db.Column(db.Integer, default=0)
    
    # Relacionamentos
    instituicao = db.relationship('Instituicao', backref='relatorios')
    
    # Índice composto único
    __table_args__ = (
        db.UniqueConstraint('instituicao_id', 'ano', 'mes', name='unique_relatorio_mensal'),
    )
    
    def to_dict(self):
        import json
        return {
            'id': self.id,
            'ano': self.ano,
            'mes': self.mes,
            'mes_nome': self.get_mes_nome(),
            'data_geracao': self.data_geracao.isoformat() if self.data_geracao else None,
            'total_entradas': self.total_entradas,
            'total_saidas': self.total_saidas,
            'saldo_mensal': self.saldo_mensal,
            'movimentos_count': self.movimentos_count,
            'dados': json.loads(self.dados_json) if self.dados_json else {}
        }
    
    def get_mes_nome(self):
        meses = [
            'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
            'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
        ]
        return meses[self.mes - 1] if 1 <= self.mes <= 12 else f'Mês {self.mes}'    

def init_dados_exemplo():
    """Inicializa dados de exemplo para a base de dados"""
    
    # Verificar se já existem dados
    if not Instituicao.query.filter_by(username='caritas').first():
        # Criar instituições de exemplo
        caritas = Instituicao(
            nome='Cáritas São Vicente',
            username='caritas',
            email='caritas@saovicente.com',
            responsavel='Director Cáritas',
            tipo_instituicao='religiosa',
            aprovada=True,
            ativa=True
        )
        caritas.set_password('sv2024')
        db.session.add(caritas)
        
        bombeiros = Instituicao(
            nome='Bombeiros Voluntários',
            username='bombeiros',
            email='bombeiros@saovicente.com',
            responsavel='Comandante Bombeiros',
            tipo_instituicao='governo',
            aprovada=True,
            ativa=True
        )
        bombeiros.set_password('sv2024')
        db.session.add(bombeiros)
        
        # Criar itens de stock de exemplo
        itens_exemplo = [
            ItemStock(nome='Arroz', unidade='kg', categoria='alimentação', descricao='Arroz branco'),
            ItemStock(nome='Feijão', unidade='kg', categoria='alimentação', descricao='Feijão encarnado'),
            ItemStock(nome='Água', unidade='litro', categoria='alimentação', descricao='Água mineral'),
            ItemStock(nome='Óleo', unidade='litro', categoria='alimentação', descricao='Óleo vegetal'),
            ItemStock(nome='Açúcar', unidade='kg', categoria='alimentação', descricao='Açúcar branco'),
            ItemStock(nome='Sabão', unidade='unidade', categoria='higiene', descricao='Sabão de lavar roupa'),
            ItemStock(nome='Pasta de dentes', unidade='unidade', categoria='higiene', descricao='Pasta dentífrica'),
            ItemStock(nome='Shampoo', unidade='unidade', categoria='higiene', descricao='Shampoo para cabelo'),
            ItemStock(nome='Camiseta', unidade='unidade', categoria='vestuário', descricao='Camiseta de algodão'),
            ItemStock(nome='Calças', unidade='unidade', categoria='vestuário', descricao='Calças de ganga'),
            ItemStock(nome='Sapatos', unidade='par', categoria='vestuário', descricao='Sapatos diversos'),
            ItemStock(nome='Colchão', unidade='unidade', categoria='mobiliário', descricao='Colchão individual'),
            ItemStock(nome='Cobertor', unidade='unidade', categoria='mobiliário', descricao='Cobertor de lã'),
            ItemStock(nome='Lençol', unidade='unidade', categoria='mobiliário', descricao='Lençol de cama')
        ]
        
        for item in itens_exemplo:
            db.session.add(item)
        
        db.session.commit()
        print("✅ Dados de exemplo criados com sucesso!")
    else:
        print("ℹ️  Dados de exemplo já existem")