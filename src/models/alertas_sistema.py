"""
Sistema de Alertas e Controles Inteligentes
Previne duplicação de doações e distribuição excessiva
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from src.models.sistema_models import db, MovimentoStock, ItemStock, Beneficiario

class AlertasSistema:
    """Classe para gerenciar alertas e controles do sistema"""
    
    # Configurações de limites (podem ser ajustadas)
    LIMITES_CATEGORIA = {
        'alimentação': {
            'periodo_dias': 30,  # Período para verificar duplicação
            'quantidade_maxima': {
                'arroz': 10,      # kg por mês
                'feijão': 8,      # kg por mês
                'óleo': 3,        # litros por mês
                'açúcar': 5,      # kg por mês
                'água': 20        # litros por mês
            }
        },
        'vestuário': {
            'periodo_dias': 90,  # 3 meses
            'quantidade_maxima': {
                'camiseta': 3,    # unidades por trimestre
                'calças': 2,      # unidades por trimestre
                'sapatos': 1      # par por trimestre
            }
        },
        'higiene': {
            'periodo_dias': 60,  # 2 meses
            'quantidade_maxima': {
                'sabão': 5,       # unidades por 2 meses
                'pasta de dentes': 2,
                'shampoo': 2
            }
        },
        'mobiliário': {
            'periodo_dias': 180,  # 6 meses
            'quantidade_maxima': {
                'colchão': 1,     # unidade por 6 meses
                'cobertor': 2,    # unidades por 6 meses
                'lençol': 3       # unidades por 6 meses
            }
        }
    }
    
    @staticmethod
    def verificar_antes_distribuicao(beneficiario_nif, item_id, quantidade_nova):
        """
        Verifica se a distribuição é apropriada antes de ser feita
        
        Returns:
            dict: {
                'pode_distribuir': bool,
                'alertas': list,
                'sugestoes': list
            }
        """
        resultado = {
            'pode_distribuir': True,
            'alertas': [],
            'sugestoes': []
        }
        
        try:
            # Buscar informações do item e beneficiário
            item = ItemStock.query.get(item_id)
            beneficiario = Beneficiario.query.get(beneficiario_nif)
            
            if not item or not beneficiario:
                resultado['pode_distribuir'] = False
                resultado['alertas'].append('Item ou beneficiário não encontrado')
                return resultado
            
            # Verificar categoria do item
            categoria = item.categoria.lower()
            nome_item = item.nome.lower()
            
            # Buscar configurações para esta categoria
            config_categoria = AlertasSistema.LIMITES_CATEGORIA.get(categoria)
            if not config_categoria:
                # Se não há limites definidos, permitir
                return resultado
            
            periodo_dias = config_categoria['periodo_dias']
            data_limite = datetime.utcnow() - timedelta(days=periodo_dias)
            
            # Buscar histórico recente do beneficiário para este item
            historico_item = MovimentoStock.query.filter(
                MovimentoStock.beneficiario_nif == beneficiario_nif,
                MovimentoStock.item_id == item_id,
                MovimentoStock.tipo_movimento == 'saida',
                MovimentoStock.data >= data_limite
            ).all()
            
            # Calcular quantidade já recebida
            quantidade_recebida = sum(mov.quantidade for mov in historico_item)
            quantidade_total = quantidade_recebida + quantidade_nova
            
            # Verificar limites específicos do item
            limites_item = config_categoria.get('quantidade_maxima', {})
            
            # Procurar limite para este item específico
            limite_especifico = None
            for nome_limite, valor_limite in limites_item.items():
                if nome_limite in nome_item:
                    limite_especifico = valor_limite
                    break
            
            if limite_especifico and quantidade_total > limite_especifico:
                resultado['alertas'].append(
                    f'⚠️ ALERTA: {beneficiario.nome} já recebeu {quantidade_recebida}{item.unidade} '
                    f'de {item.nome} nos últimos {periodo_dias} dias. '
                    f'Com esta distribuição ({quantidade_nova}{item.unidade}), '
                    f'totalizará {quantidade_total}{item.unidade}, '
                    f'excedendo o limite recomendado de {limite_especifico}{item.unidade}.'
                )
                
                # Sugerir quantidade alternativa
                quantidade_sugerida = max(0, limite_especifico - quantidade_recebida)
                if quantidade_sugerida > 0:
                    resultado['sugestoes'].append(
                        f'💡 Sugestão: Distribuir apenas {quantidade_sugerida}{item.unidade} '
                        f'de {item.nome} para não exceder o limite.'
                    )
                else:
                    resultado['sugestoes'].append(
                        f'💡 Sugestão: Considerar distribuir outro item da categoria {categoria} '
                        f'ou aguardar alguns dias antes de nova distribuição.'
                    )
            
            # Verificar distribuições muito frequentes (mesmo item em poucos dias)
            historico_recente = MovimentoStock.query.filter(
                MovimentoStock.beneficiario_nif == beneficiario_nif,
                MovimentoStock.item_id == item_id,
                MovimentoStock.tipo_movimento == 'saida',
                MovimentoStock.data >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            if historico_recente > 0:
                resultado['alertas'].append(
                    f'📅 ATENÇÃO: {beneficiario.nome} já recebeu {item.nome} '
                    f'nos últimos 7 dias. Verificar se é realmente necessário.'
                )
            
            # Verificar se beneficiário recebeu muitos itens recentemente
            total_recente = MovimentoStock.query.filter(
                MovimentoStock.beneficiario_nif == beneficiario_nif,
                MovimentoStock.tipo_movimento == 'saida',
                MovimentoStock.data >= datetime.utcnow() - timedelta(days=7)
            ).count()
            
            if total_recente >= 5:
                resultado['alertas'].append(
                    f'📊 DISTRIBUIÇÃO FREQUENTE: {beneficiario.nome} já recebeu '
                    f'{total_recente} itens nos últimos 7 dias. '
                    f'Considerar priorizar outros beneficiários.'
                )
            
            # Buscar beneficiários com menos ajuda para sugerir
            beneficiarios_menos_ajuda = AlertasSistema.buscar_beneficiarios_menos_ajuda(categoria, 5)
            if beneficiarios_menos_ajuda:
                nomes = [b['nome'] for b in beneficiarios_menos_ajuda[:3]]
                resultado['sugestoes'].append(
                    f'🎯 Considerar priorizar: {", ".join(nomes)} '
                    f'(receberam menos itens de {categoria} recentemente)'
                )
            
            return resultado
            
        except Exception as e:
            resultado['pode_distribuir'] = False
            resultado['alertas'].append(f'Erro ao verificar distribuição: {str(e)}')
            return resultado
    
    @staticmethod
    def buscar_beneficiarios_menos_ajuda(categoria=None, limite=10):
        """
        Busca beneficiários que receberam menos ajuda recentemente
        
        Args:
            categoria (str): Categoria específica ou None para todas
            limite (int): Número máximo de beneficiários a retornar
            
        Returns:
            list: Lista de beneficiários com menos ajuda
        """
        try:
            # Período para análise (últimos 30 dias)
            data_limite = datetime.utcnow() - timedelta(days=30)
            
            # Query base
            query = db.session.query(
                Beneficiario.nif,
                Beneficiario.nome,
                Beneficiario.zona_residencia,
                func.count(MovimentoStock.id).label('total_ajudas')
            ).outerjoin(
                MovimentoStock,
                (MovimentoStock.beneficiario_nif == Beneficiario.nif) &
                (MovimentoStock.tipo_movimento == 'saida') &
                (MovimentoStock.data >= data_limite)
            )
            
            # Filtrar por categoria se especificada
            if categoria:
                query = query.join(
                    ItemStock,
                    MovimentoStock.item_id == ItemStock.id
                ).filter(
                    ItemStock.categoria.ilike(f'%{categoria}%')
                )
            
            # Agrupar e ordenar
            beneficiarios = query.group_by(
                Beneficiario.nif,
                Beneficiario.nome,
                Beneficiario.zona_residencia
            ).order_by(
                'total_ajudas'
            ).limit(limite).all()
            
            return [
                {
                    'nif': b.nif,
                    'nome': b.nome,
                    'zona': b.zona_residencia,
                    'total_ajudas': b.total_ajudas
                }
                for b in beneficiarios
            ]
            
        except Exception as e:
            print(f"Erro ao buscar beneficiários com menos ajuda: {str(e)}")
            return []
    
    @staticmethod
    def gerar_relatorio_distribuicao_equitativa():
        """
        Gera relatório de distribuição equitativa
        
        Returns:
            dict: Relatório com estatísticas de distribuição
        """
        try:
            # Período para análise (últimos 30 dias)
            data_limite = datetime.utcnow() - timedelta(days=30)
            
            # Estatísticas gerais
            total_beneficiarios = Beneficiario.query.count()
            
            beneficiarios_atendidos = db.session.query(
                func.count(func.distinct(MovimentoStock.beneficiario_nif))
            ).filter(
                MovimentoStock.tipo_movimento == 'saida',
                MovimentoStock.data >= data_limite
            ).scalar()
            
            # Distribuição por zona
            distribuicao_zona = db.session.query(
                Beneficiario.zona_residencia,
                func.count(MovimentoStock.id).label('total_distribuicoes')
            ).join(
                MovimentoStock,
                MovimentoStock.beneficiario_nif == Beneficiario.nif
            ).filter(
                MovimentoStock.tipo_movimento == 'saida',
                MovimentoStock.data >= data_limite
            ).group_by(
                Beneficiario.zona_residencia
            ).all()
            
            # Top 10 beneficiários que mais receberam
            top_beneficiarios = db.session.query(
                Beneficiario.nome,
                Beneficiario.nif,
                func.count(MovimentoStock.id).label('total_ajudas')
            ).join(
                MovimentoStock,
                MovimentoStock.beneficiario_nif == Beneficiario.nif
            ).filter(
                MovimentoStock.tipo_movimento == 'saida',
                MovimentoStock.data >= data_limite
            ).group_by(
                Beneficiario.nif,
                Beneficiario.nome
            ).order_by(
                func.count(MovimentoStock.id).desc()
            ).limit(10).all()
            
            return {
                'periodo': '30 dias',
                'total_beneficiarios': total_beneficiarios,
                'beneficiarios_atendidos': beneficiarios_atendidos,
                'cobertura_percentual': round((beneficiarios_atendidos / total_beneficiarios) * 100, 1) if total_beneficiarios > 0 else 0,
                'distribuicao_por_zona': [
                    {
                        'zona': d.zona_residencia or 'Não especificada',
                        'total_distribuicoes': d.total_distribuicoes
                    }
                    for d in distribuicao_zona
                ],
                'top_beneficiarios': [
                    {
                        'nome': b.nome,
                        'nif': b.nif,
                        'total_ajudas': b.total_ajudas
                    }
                    for b in top_beneficiarios
                ]
            }
            
        except Exception as e:
            return {
                'erro': f'Erro ao gerar relatório: {str(e)}'
            }
    
    @staticmethod
    def configurar_limites_personalizados(categoria, item, quantidade_maxima, periodo_dias):
        """
        Permite configurar limites personalizados
        
        Args:
            categoria (str): Categoria do item
            item (str): Nome do item
            quantidade_maxima (int): Quantidade máxima permitida
            periodo_dias (int): Período em dias para o limite
        """
        if categoria not in AlertasSistema.LIMITES_CATEGORIA:
            AlertasSistema.LIMITES_CATEGORIA[categoria] = {
                'periodo_dias': periodo_dias,
                'quantidade_maxima': {}
            }
        
        AlertasSistema.LIMITES_CATEGORIA[categoria]['quantidade_maxima'][item.lower()] = quantidade_maxima
        AlertasSistema.LIMITES_CATEGORIA[categoria]['periodo_dias'] = periodo_dias
