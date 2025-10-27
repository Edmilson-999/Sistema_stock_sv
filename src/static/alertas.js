/**
 * Sistema de Alertas e Controles Inteligentes
 * Integração com a interface do usuário
 */

class SistemaAlertas {
    constructor() {
        this.alertasAtivos = [];
    }

    /**
     * Verifica se uma distribuição é apropriada antes de ser feita
     */
    async verificarDistribuicao(beneficiarioNif, itemId, quantidade) {
        try {
            const response = await fetch('/api/alertas/verificar-distribuicao', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    beneficiario_nif: beneficiarioNif,
                    item_id: itemId,
                    quantidade: quantidade
                })
            });

            const data = await response.json();
            
            if (data.success) {
                return data.verificacao;
            } else {
                throw new Error(data.error || 'Erro ao verificar distribuição');
            }
        } catch (error) {
            console.error('Erro ao verificar distribuição:', error);
            return {
                pode_distribuir: true,
                alertas: [],
                sugestoes: []
            };
        }
    }

    /**
     * Busca beneficiários que receberam menos ajuda
     */
    async buscarBeneficiariosMenosAjuda(categoria = null, limite = 10) {
        try {
            const params = new URLSearchParams();
            if (categoria) params.append('categoria', categoria);
            params.append('limite', limite);

            const response = await fetch(`/api/alertas/beneficiarios-menos-ajuda?${params}`);
            const data = await response.json();

            if (data.success) {
                return data.beneficiarios;
            } else {
                throw new Error(data.error || 'Erro ao buscar beneficiários');
            }
        } catch (error) {
            console.error('Erro ao buscar beneficiários com menos ajuda:', error);
            return [];
        }
    }

    /**
     * Mostra modal de alerta com opções
     */
    mostrarModalAlerta(alertas, sugestoes, beneficiario, item, quantidade, callback) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content alerta-modal">
                <div class="modal-header">
                    <h3>⚠️ Alertas de Distribuição</h3>
                </div>
                
                <div class="modal-body">
                    <div class="distribuicao-info">
                        <p><strong>Beneficiário:</strong> ${beneficiario.nome} (${beneficiario.nif})</p>
                        <p><strong>Item:</strong> ${quantidade} ${item.unidade} de ${item.nome}</p>
                        ${beneficiario.zona ? `<p><strong>Zona:</strong> ${beneficiario.zona}</p>` : ''}
                    </div>

                    ${alertas.length > 0 ? `
                        <div class="alertas-section">
                            <h4>🚨 Alertas:</h4>
                            <ul class="alertas-list">
                                ${alertas.map(alerta => `<li class="alerta-item">${alerta}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}

                    ${sugestoes.length > 0 ? `
                        <div class="sugestoes-section">
                            <h4>💡 Sugestões:</h4>
                            <ul class="sugestoes-list">
                                ${sugestoes.map(sugestao => `<li class="sugestao-item">${sugestao}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>

                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">
                        ❌ Cancelar
                    </button>
                    <button class="btn btn-warning" onclick="sistemaAlertas.prosseguirComAlerta(this)">
                        ⚠️ Prosseguir Mesmo Assim
                    </button>
                </div>
            </div>
        `;

        // Adicionar callback ao botão de prosseguir
        modal.querySelector('.btn-warning').addEventListener('click', () => {
            modal.remove();
            if (callback) callback(true); // true = forçar distribuição
        });

        document.body.appendChild(modal);
    }

    /**
     * Mostra sugestões de beneficiários com menos ajuda
     */
    async mostrarSugestoesBeneficiarios(categoria) {
        const beneficiarios = await this.buscarBeneficiariosMenosAjuda(categoria, 10);
        
        if (beneficiarios.length === 0) {
            this.mostrarNotificacao('Nenhuma sugestão disponível no momento.', 'info');
            return;
        }

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content sugestoes-modal">
                <div class="modal-header">
                    <h3>🎯 Beneficiários Prioritários</h3>
                    <p>Beneficiários que receberam menos ajuda recentemente${categoria ? ` na categoria ${categoria}` : ''}:</p>
                </div>
                
                <div class="modal-body">
                    <div class="beneficiarios-grid">
                        ${beneficiarios.map(b => `
                            <div class="beneficiario-card" data-nif="${b.nif}">
                                <div class="beneficiario-info">
                                    <strong>${b.nome}</strong>
                                    <small>NIF: ${b.nif}</small>
                                    ${b.zona ? `<small>Zona: ${b.zona}</small>` : ''}
                                </div>
                                <div class="beneficiario-stats">
                                    <span class="ajudas-count">${b.total_ajudas} ajudas</span>
                                </div>
                                <button class="btn btn-sm btn-primary" onclick="sistemaAlertas.selecionarBeneficiario('${b.nif}', '${b.nome}')">
                                    Selecionar
                                </button>
                            </div>
                        `).join('')}
                    </div>
                </div>

                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">
                        Fechar
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    }

    /**
     * Seleciona um beneficiário sugerido
     */
    selecionarBeneficiario(nif, nome) {
        // Preencher o campo de beneficiário no formulário
        const nifInput = document.querySelector('input[name="beneficiario_nif"]');
        const nomeDisplay = document.querySelector('.beneficiario-selecionado');
        
        if (nifInput) {
            nifInput.value = nif;
        }
        
        if (nomeDisplay) {
            nomeDisplay.textContent = `${nome} (${nif})`;
        }

        // Fechar modal
        document.querySelector('.modal-overlay').remove();
        
        this.mostrarNotificacao(`Beneficiário ${nome} selecionado!`, 'success');
    }

    /**
     * Mostra relatório de distribuição equitativa
     */
    async mostrarRelatorioDistribuicao() {
        try {
            const response = await fetch('/api/alertas/relatorio-distribuicao');
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Erro ao carregar relatório');
            }

            const relatorio = data.relatorio;
            
            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal-content relatorio-modal">
                    <div class="modal-header">
                        <h3>📊 Relatório de Distribuição Equitativa</h3>
                        <p>Análise dos últimos ${relatorio.periodo}</p>
                    </div>
                    
                    <div class="modal-body">
                        <div class="stats-grid">
                            <div class="stat-card">
                                <h4>${relatorio.total_beneficiarios}</h4>
                                <p>Total de Beneficiários</p>
                            </div>
                            <div class="stat-card">
                                <h4>${relatorio.beneficiarios_atendidos}</h4>
                                <p>Beneficiários Atendidos</p>
                            </div>
                            <div class="stat-card">
                                <h4>${relatorio.cobertura_percentual}%</h4>
                                <p>Cobertura</p>
                            </div>
                        </div>

                        ${relatorio.distribuicao_por_zona && relatorio.distribuicao_por_zona.length > 0 ? `
                            <div class="zonas-section">
                                <h4>📍 Distribuição por Zona:</h4>
                                <div class="zonas-list">
                                    ${relatorio.distribuicao_por_zona.map(zona => `
                                        <div class="zona-item">
                                            <span class="zona-nome">${zona.zona}</span>
                                            <span class="zona-count">${zona.total_distribuicoes} distribuições</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}

                        ${relatorio.top_beneficiarios && relatorio.top_beneficiarios.length > 0 ? `
                            <div class="top-section">
                                <h4>🏆 Beneficiários que Mais Receberam:</h4>
                                <div class="top-list">
                                    ${relatorio.top_beneficiarios.map((b, index) => `
                                        <div class="top-item">
                                            <span class="posicao">${index + 1}º</span>
                                            <span class="nome">${b.nome}</span>
                                            <span class="nif">(${b.nif})</span>
                                            <span class="count">${b.total_ajudas} ajudas</span>
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>

                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()">
                            Fechar
                        </button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);

        } catch (error) {
            console.error('Erro ao mostrar relatório:', error);
            this.mostrarNotificacao('Erro ao carregar relatório de distribuição.', 'error');
        }
    }

    /**
     * Mostra notificação temporária
     */
    mostrarNotificacao(mensagem, tipo = 'info') {
        const notificacao = document.createElement('div');
        notificacao.className = `notificacao notificacao-${tipo}`;
        notificacao.innerHTML = `
            <div class="notificacao-content">
                <span class="notificacao-icon">
                    ${tipo === 'success' ? '✅' : tipo === 'error' ? '❌' : tipo === 'warning' ? '⚠️' : 'ℹ️'}
                </span>
                <span class="notificacao-text">${mensagem}</span>
                <button class="notificacao-close" onclick="this.parentElement.parentElement.remove()">×</button>
            </div>
        `;

        document.body.appendChild(notificacao);

        // Remover automaticamente após 5 segundos
        setTimeout(() => {
            if (notificacao.parentElement) {
                notificacao.remove();
            }
        }, 5000);
    }
}

// Instância global do sistema de alertas
const sistemaAlertas = new SistemaAlertas();

// CSS para os alertas
const alertasCSS = `
<style>
.alerta-modal, .sugestoes-modal, .relatorio-modal {
    max-width: 600px;
    max-height: 80vh;
    overflow-y: auto;
}

.distribuicao-info {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.alertas-section, .sugestoes-section {
    margin: 20px 0;
}

.alertas-list, .sugestoes-list {
    list-style: none;
    padding: 0;
}

.alerta-item, .sugestao-item {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 6px;
    padding: 12px;
    margin: 8px 0;
    font-size: 14px;
    line-height: 1.4;
}

.alerta-item {
    background: #f8d7da;
    border-color: #f5c6cb;
}

.beneficiarios-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
    max-height: 400px;
    overflow-y: auto;
}

.beneficiario-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    background: white;
    transition: transform 0.2s;
}

.beneficiario-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.beneficiario-info strong {
    display: block;
    margin-bottom: 5px;
}

.beneficiario-info small {
    display: block;
    color: #666;
    font-size: 12px;
}

.ajudas-count {
    background: #e3f2fd;
    color: #1976d2;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 15px;
    margin-bottom: 25px;
}

.stat-card {
    text-align: center;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.stat-card h4 {
    font-size: 2em;
    margin: 0;
    color: #2e7d32;
}

.zonas-list, .top-list {
    max-height: 200px;
    overflow-y: auto;
}

.zona-item, .top-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border-bottom: 1px solid #eee;
}

.posicao {
    font-weight: bold;
    color: #ff9800;
    margin-right: 10px;
}

.notificacao {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    min-width: 300px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    animation: slideIn 0.3s ease-out;
}

.notificacao-success { background: #d4edda; border: 1px solid #c3e6cb; color: #155724; }
.notificacao-error { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; }
.notificacao-warning { background: #fff3cd; border: 1px solid #ffeaa7; color: #856404; }
.notificacao-info { background: #d1ecf1; border: 1px solid #bee5eb; color: #0c5460; }

.notificacao-content {
    display: flex;
    align-items: center;
    padding: 15px;
}

.notificacao-icon {
    margin-right: 10px;
    font-size: 18px;
}

.notificacao-text {
    flex: 1;
}

.notificacao-close {
    background: none;
    border: none;
    font-size: 20px;
    cursor: pointer;
    margin-left: 10px;
}

@keyframes slideIn {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}
</style>
`;

// Adicionar CSS ao documento
document.head.insertAdjacentHTML('beforeend', alertasCSS);