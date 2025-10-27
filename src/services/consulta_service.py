"""
Serviço para consultas cruzadas entre instituições
"""

from src.models.sistema_models import db, Beneficiario, MovimentoStock, Instituicao
from sqlalchemy import or_, and_

class ConsultaService:
    """Serviço para consultas cruzadas de beneficiários"""
    
    @staticmethod
    def consultar_beneficiario_por_nif(nif, instituicao_requisitante_id):
        """
        Consulta um beneficiário por NIF, mostrando dados da instituição atual
        e informações básicas de outras instituições
        
        Args:
            nif (str): NIF do beneficiário
            instituicao_requisitante_id (int): ID da instituição que está consultando
            
        Returns:
            dict: Dados completos do beneficiário
        """
        try:
            # Buscar beneficiário (pode ser de qualquer instituição)
            beneficiario = Beneficiario.query.get(nif)
            
            if not beneficiario:
                return {
                    'encontrado': False,
                    'mensagem': 'Beneficiário não encontrado no sistema'
                }
            
            # Buscar histórico completo (todas as instituições)
            historico_completo = MovimentoStock.query.filter_by(
                beneficiario_nif=nif
            ).order_by(MovimentoStock.data.desc()).all()
            
            # Separar histórico da instituição atual vs outras instituições
            historico_instituicao_atual = []
            historico_outras_instituicoes = []
            instituicoes_que_ajudaram = set()
            
            for movimento in historico_completo:
                movimento_dict = movimento.to_dict()
                
                if movimento.instituicao_id == instituicao_requisitante_id:
                    historico_instituicao_atual.append(movimento_dict)
                else:
                    # Para outras instituições, mostrar apenas informações básicas
                    movimento_restrito = {
                        'data': movimento.data,
                        'item_nome': movimento.item.nome,
                        'quantidade': movimento.quantidade,
                        'instituicao_nome': movimento.instituicao.nome,
                        'tipo_instituicao': movimento.instituicao.tipo_instituicao
                    }
                    historico_outras_instituicoes.append(movimento_restrito)
                    instituicoes_que_ajudaram.add(movimento.instituicao.nome)
            
            # Informações da instituição de registro
            instituicao_registro_info = None
            if beneficiario.instituicao_registro:
                instituicao_registro_info = {
                    'nome': beneficiario.instituicao_registro.nome,
                    'tipo': beneficiario.instituicao_registro.tipo_instituicao
                }
            
            return {
                'encontrado': True,
                'beneficiario': beneficiario.to_dict(),
                'instituicao_registro': instituicao_registro_info,
                'historico_instituicao_atual': historico_instituicao_atual,
                'historico_outras_instituicoes': historico_outras_instituicoes,
                'total_ajudas_instituicao_atual': len(historico_instituicao_atual),
                'total_ajudas_outras_instituicoes': len(historico_outras_instituicoes),
                'instituicoes_que_ajudaram': list(instituicoes_que_ajudaram),
                'avisos': ConsultaService.gerar_avisos_consulta(
                    beneficiario, historico_completo, instituicao_requisitante_id
                )
            }
            
        except Exception as e:
            return {
                'encontrado': False,
                'erro': f'Erro na consulta: {str(e)}'
            }
    
    @staticmethod
    def gerar_avisos_consulta(beneficiario, historico_completo, instituicao_requisitante_id):
        """
        Gera alertas importantes sobre o beneficiário
        """
        avisos = []
        
        # Verificar se já recebeu ajuda recentemente
        from datetime import datetime, timedelta
        data_limite = datetime.utcnow() - timedelta(days=7)
        
        ajudas_recentes = [m for m in historico_completo 
                          if m.data >= data_limite and m.tipo_movimento == 'saida']
        
        if ajudas_recentes:
            instituicoes_recentes = set(m.instituicao.nome for m in ajudas_recentes)
            avisos.append(
                f"⚠️ Recebeu {len(ajudas_recentes)} ajudas nos últimos 7 dias de: {', '.join(instituicoes_recentes)}"
            )
        
        # Verificar se a instituição atual já ajudou recentemente
        ajudas_instituicao_atual = [m for m in ajudas_recentes 
                                   if m.instituicao_id == instituicao_requisitante_id]
        
        if ajudas_instituicao_atual:
            avisos.append(
                f"📅 Sua instituição já ajudou este beneficiário {len(ajudas_instituicao_atual)} vez(es) na última semana"
            )
        
        return avisos
    
    @staticmethod
    def buscar_beneficiarios_instituicao(instituicao_id, search=''):
        """
        Busca apenas beneficiários registrados pela instituição atual
        """
        query = Beneficiario.query.filter_by(
            instituicao_registro_id=instituicao_id
        )
        
        if search:
            query = query.filter(
                or_(
                    Beneficiario.nome.ilike(f'%{search}%'),
                    Beneficiario.nif.ilike(f'%{search}%'),
                    Beneficiario.zona_residencia.ilike(f'%{search}%')
                )
            )
        
        return query.order_by(Beneficiario.nome).all()
    
    @staticmethod
    def registrar_novo_beneficiario(dados, instituicao_id):
        """
        Registra um novo beneficiário associado à instituição atual
        """
        try:
            # Verificar se já existe beneficiário com este NIF
            if Beneficiario.query.get(dados['nif']):
                return {
                    'sucesso': False,
                    'erro': 'Já existe um beneficiário com este NIF no sistema'
                }
            
            beneficiario = Beneficiario(
                nif=dados['nif'],
                nome=dados['nome'],
                idade=dados.get('idade'),
                endereco=dados.get('endereco'),
                contacto=dados.get('contacto'),
                num_agregado=dados.get('num_agregado'),
                necessidades=dados.get('necessidades'),
                observacoes=dados.get('observacoes'),
                zona_residencia=dados.get('zona_residencia'),
                perdas_pedidos=dados.get('perdas_pedidos'),
                instituicao_registro_id=instituicao_id
            )
            
            db.session.add(beneficiario)
            db.session.commit()
            
            return {
                'sucesso': True,
                'beneficiario': beneficiario.to_dict()
            }
            
        except Exception as e:
            db.session.rollback()
            return {
                'sucesso': False,
                'erro': f'Erro ao registrar beneficiário: {str(e)}'
            }