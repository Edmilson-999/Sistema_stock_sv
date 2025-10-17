/**
 * Sistema de Registro de Instituições
 * Interface para registro e aprovação de novas instituições
 */

class SistemaRegistro {
    constructor() {
        this.tiposInstituicao = [];
        this.instituicoesData = [];
        this.carregarTiposInstituicao();
    }

    /**
     * Carrega os tipos de instituição disponíveis
     */
    async carregarTiposInstituicao() {
        try {
            const response = await fetch('/api/auth/tipos-instituicao');
            const data = await response.json();
            this.tiposInstituicao = data.tipos;
        } catch (error) {
            console.error('Erro ao carregar tipos de instituição:', error);
        }
    }

    /**
     * Tenta acesso ao painel administrativo
     */
    async tentarAcessoAdmin() {
        // Mostrar modal de login administrativo
        this.mostrarLoginAdmin();
    }

    /**
     * Mostra modal de login para administrador
     */
    mostrarLoginAdmin() {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content admin-login-modal">
                <div class="modal-header">
                    <h3>🛡️ Acesso Administrativo</h3>
                    <p>Insira as credenciais de administrador</p>
                </div>
                
                <form id="formLoginAdmin" class="admin-login-form">
                    <div class="form-group">
                        <label for="adminUsername">Username</label>
                        <input type="text" id="adminUsername" name="username" required>
                    </div>

                    <div class="form-group">
                        <label for="adminPassword">Password</label>
                        <input type="password" id="adminPassword" name="password" required>
                    </div>

                    <div class="form-errors" id="adminLoginErrors" style="display: none;"></div>

                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="sistemaRegistro.fecharModalRegistro(this)">
                            Cancelar
                        </button>
                        <button type="submit" class="btn btn-primary">
                            🔐 Entrar
                        </button>
                    </div>
                </form>
            </div>
        `;

        // Adicionar evento de submit
        const form = modal.querySelector('#formLoginAdmin');
        form.addEventListener('submit', (e) => this.fazerLoginAdmin(e));

        document.body.appendChild(modal);
    }

    /**
     * Faz login como administrador
     */
    async fazerLoginAdmin(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const dados = Object.fromEntries(formData.entries());

        // Limpar erros anteriores
        this.limparErrosAdmin();

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });

            const data = await response.json();

            if (data.success) {
                // Verificar se o usuário é administrador
                if (data.instituicao.username === 'admin' || data.instituicao.username === 'caritas') {
                    // Fechar modal de login
                    form.closest('.modal-overlay').remove();
                    // Mostrar gestão de instituições
                    this.mostrarGestaoInstituicoes();
                } else {
                    this.mostrarErroAdmin('Acesso negado. Apenas administradores podem acessar este painel.');
                    // Fazer logout já que não é admin
                    await fetch('/api/auth/logout', { method: 'POST' });
                }
            } else {
                this.mostrarErroAdmin(data.error || 'Credenciais inválidas');
            }
        } catch (error) {
            console.error('Erro no login admin:', error);
            this.mostrarErroAdmin('Erro de conexão. Tente novamente.');
        }
    }

    /**
     * Mostra gestão completa de instituições (aprovadas e pendentes)
     */
    async mostrarGestaoInstituicoes() {
        try {
            const response = await fetch('/api/auth/admin/todas-instituicoes', {
                credentials: 'include'
            });

            if (response.status === 401 || response.status === 403) {
                alert('Acesso negado. Você não tem permissões de administrador.');
                return;
            }

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Erro ao carregar instituições');
            }

            // Esconder a tela de login principal
            const loginSection = document.getElementById('loginSection');
            if (loginSection) loginSection.style.display = 'none';

            const modal = document.createElement('div');
            modal.className = 'modal-overlay';
            modal.innerHTML = `
                <div class="modal-content admin-modal">
                    <div class="modal-header">
                        <h3>🛡️ Gestão de Instituições</h3>
                        <p>Gerir todas as instituições do sistema</p>
                        <div class="admin-info">
                            <small>Logado como: ${data.admin?.nome || 'Administrador'}</small>
                            <button class="btn btn-small btn-danger" onclick="sistemaRegistro.sairPainelAdmin()">
                                🚪 Sair
                            </button>
                        </div>
                    </div>
                    
                    <div class="modal-body">
                        <div class="tabs">
                            <button class="tab-button active" onclick="sistemaRegistro.mostrarAba('pendentes', event)">
                                ⏳ Pendentes (${data.instituicoes.filter(i => i.estado === 'Pendente').length})
                            </button>
                            <button class="tab-button" onclick="sistemaRegistro.mostrarAba('aprovadas', event)">
                                ✅ Aprovadas (${data.instituicoes.filter(i => i.estado === 'Aprovada').length})
                            </button>
                            <button class="tab-button" onclick="sistemaRegistro.mostrarAba('todas', event)">
                                📋 Todas (${data.instituicoes.length})
                            </button>
                        </div>
                        
                        <div id="abaConteudo">
                            <!-- Conteúdo será carregado aqui -->
                        </div>
                    </div>

                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="sistemaRegistro.sairPainelAdmin()">
                            Fechar
                        </button>
                    </div>
                </div>
            `;

            document.body.appendChild(modal);
            
            // Guardar dados das instituições
            this.instituicoesData = data.instituicoes;
            
            // Mostrar aba padrão
            this.mostrarAba('pendentes', null);

        } catch (error) {
            console.error('Erro ao carregar gestão de instituições:', error);
            alert('Erro ao carregar gestão de instituições: ' + error.message);
        }
    }

    /**
     * Mostra diferentes abas na gestão de instituições
     */
    mostrarAba(aba, event = null) {
        const conteudo = document.getElementById('abaConteudo');
        if (!conteudo) return;

        let instituicoesFiltradas = [];
        let titulo = '';

        switch (aba) {
            case 'pendentes':
                instituicoesFiltradas = this.instituicoesData.filter(i => i.estado === 'Pendente');
                titulo = 'Instituições Pendentes de Aprovação';
                break;
            case 'aprovadas':
                instituicoesFiltradas = this.instituicoesData.filter(i => i.estado === 'Aprovada');
                titulo = 'Instituições Aprovadas';
                break;
            case 'todas':
                instituicoesFiltradas = this.instituicoesData;
                titulo = 'Todas as Instituições';
                break;
        }

        // Atualizar tabs ativas (se event estiver disponível)
        if (event) {
            document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
        } else {
            // Fallback: atualizar baseado no nome da aba
            document.querySelectorAll('.tab-button').forEach(btn => {
                btn.classList.remove('active');
                if (btn.textContent.includes(aba.charAt(0).toUpperCase() + aba.slice(1))) {
                    btn.classList.add('active');
                }
            });
        }

        if (instituicoesFiltradas.length === 0) {
            conteudo.innerHTML = `
                <div class="empty-state">
                    <p>✅ Nenhuma instituição encontrada</p>
                </div>
            `;
            return;
        }

        let html = `
            <h4 style="margin-bottom: 20px; color: #2d5a27;">${titulo}</h4>
            <div class="instituicoes-lista">
        `;

        instituicoesFiltradas.forEach(inst => {
            const dataCriacao = new Date(inst.data_criacao).toLocaleDateString('pt-PT');
            
            html += `
                <div class="instituicao-card" data-id="${inst.id}">
                    <div class="instituicao-header">
                        <h4>${inst.nome}</h4>
                        <div class="instituicao-status">
                            <span class="status-badge status-${inst.estado.toLowerCase()}">${inst.estado}</span>
                            ${inst.pode_eliminar ? `
                                <button class="btn btn-danger btn-small" onclick="sistemaRegistro.eliminarInstituicao(${inst.id}, '${inst.nome.replace(/'/g, "\\'")}')">
                                    🗑️ Eliminar
                                </button>
                            ` : `
                                <span class="badge-protected">🔒 Protegida</span>
                            `}
                        </div>
                    </div>
                    
                    <div class="instituicao-details">
                        <p><strong>Username:</strong> ${inst.username}</p>
                        <p><strong>Email:</strong> ${inst.email}</p>
                        <p><strong>Responsável:</strong> ${inst.responsavel}</p>
                        <p><strong>Tipo:</strong> ${inst.tipo_instituicao}</p>
                        ${inst.telefone ? `<p><strong>Telefone:</strong> ${inst.telefone}</p>` : ''}
                        ${inst.documento_legal ? `<p><strong>Documento:</strong> ${inst.documento_legal}</p>` : ''}
                        <p><strong>Data de Registo:</strong> ${dataCriacao}</p>
                        ${inst.descricao ? `<p><strong>Descrição:</strong> ${inst.descricao}</p>` : ''}
                    </div>
                    
                    ${inst.estado === 'Pendente' ? `
                        <div class="instituicao-actions">
                            <button class="btn btn-success" onclick="sistemaRegistro.aprovarInstituicao(${inst.id})">
                                ✅ Aprovar
                            </button>
                            <button class="btn btn-danger" onclick="sistemaRegistro.rejeitarInstituicao(${inst.id})">
                                ❌ Rejeitar
                            </button>
                        </div>
                    ` : ''}
                </div>
            `;
        });

        html += '</div>';
        conteudo.innerHTML = html;
    }

    /**
     * Atualiza contadores nas tabs
     */
    atualizarContadoresTabs() {
        const pendentes = this.instituicoesData.filter(i => i.estado === 'Pendente').length;
        const aprovadas = this.instituicoesData.filter(i => i.estado === 'Aprovada').length;
        const todas = this.instituicoesData.length;

        document.querySelectorAll('.tab-button').forEach((btn, index) => {
            if (index === 0) btn.textContent = `⏳ Pendentes (${pendentes})`;
            if (index === 1) btn.textContent = `✅ Aprovadas (${aprovadas})`;
            if (index === 2) btn.textContent = `📋 Todas (${todas})`;
        });
    }

    /**
     * Recarrega a aba atualmente selecionada
     */
    recarregarAbaAtual() {
        const abaAtiva = document.querySelector('.tab-button.active');
        if (!abaAtiva) return;
        
        // Determinar qual aba está ativa baseado no texto
        const textoAba = abaAtiva.textContent;
        
        if (textoAba.includes('Pendentes')) {
            this.mostrarAba('pendentes', null);
        } else if (textoAba.includes('Aprovadas')) {
            this.mostrarAba('aprovadas', null);
        } else if (textoAba.includes('Todas')) {
            this.mostrarAba('todas', null);
        }
    }

    /**
     * Atualiza os dados da instituição após aprovação/rejeição
     */
    atualizarInstituicaoAposAcao(instituicaoId, aprovada) {
        console.log('🔍 Atualizando instituição após ação:', instituicaoId, aprovada);
        
        // Encontrar a instituição nos dados
        const instituicaoIndex = this.instituicoesData.findIndex(inst => inst.id === instituicaoId);
        
        if (instituicaoIndex !== -1) {
            if (aprovada) {
                // Se foi aprovada, atualizar o estado
                this.instituicoesData[instituicaoIndex].aprovada = true;
                this.instituicoesData[instituicaoIndex].estado = 'Aprovada';
                console.log('✅ Instituição aprovada - atualizando estado');
            } else {
                // Se foi rejeitada, atualizar o estado
                this.instituicoesData[instituicaoIndex].ativa = false;
                this.instituicoesData[instituicaoIndex].estado = 'Rejeitada';
                console.log('❌ Instituição rejeitada - atualizando estado');
            }
            
            // Recarregar a aba atual
            this.recarregarAbaAtual();
            
            // Atualizar contadores
            this.atualizarContadoresTabs();
            
            console.log('🔄 Interface atualizada com sucesso');
        } else {
            console.log('⚠️ Instituição não encontrada nos dados:', instituicaoId);
        }
    }

    /**
     * Aprova uma instituição
     */
    async aprovarInstituicao(instituicaoId) {
        console.log('🔍 Aprovar instituição:', instituicaoId);
        console.log('📊 Dados antes:', this.instituicoesData.length, 'instituições');

        if (!confirm('Tem certeza que deseja aprovar esta instituição?')) return;

        try {
            const response = await fetch(`/api/auth/admin/aprovar-instituicao/${instituicaoId}`, {
                method: 'POST',
                credentials: 'include'
            });

            const data = await response.json();

            if (data.success) {
                // ✅ ATUALIZAÇÃO: Atualizar os dados localmente em vez de apenas remover o card
                this.atualizarInstituicaoAposAcao(instituicaoId, true);
                
                this.mostrarNotificacao('Instituição aprovada com sucesso!', 'success');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Erro ao aprovar instituição:', error);
            this.mostrarNotificacao('Erro ao aprovar instituição: ' + error.message, 'error');
        }
    }

    /**
     * Rejeita uma instituição
     */
    async rejeitarInstituicao(instituicaoId) {
        console.log('🔍 Rejeitar instituição:', instituicaoId);
        console.log('📊 Dados antes:', this.instituicoesData.length, 'instituições');

        const motivo = prompt('Motivo da rejeição:');
        if (!motivo) return;

        try {
            const response = await fetch(`/api/auth/admin/rejeitar-instituicao/${instituicaoId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ motivo }),
                credentials: 'include'
            });

            const data = await response.json();

            if (data.success) {
                // ✅ ATUALIZAÇÃO: Atualizar os dados localmente
                this.atualizarInstituicaoAposAcao(instituicaoId, false);
                
                this.mostrarNotificacao('Instituição rejeitada', 'warning');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Erro ao rejeitar instituição:', error);
            this.mostrarNotificacao('Erro ao rejeitar instituição: ' + error.message, 'error');
        }
    }

    /**
     * Elimina uma instituição
     */
    async eliminarInstituicao(instituicaoId, nomeInstituicao) {
        console.log('🔍 Eliminar instituição:', instituicaoId);

        if (!confirm(`Tem certeza que deseja ELIMINAR a instituição "${nomeInstituicao}"?\n\n⚠️ Esta ação é irreversível e eliminará todos os dados associados.`)) {
            return;
        }

        try {
            const response = await fetch(`/api/auth/admin/eliminar-instituicao/${instituicaoId}`, {
                method: 'DELETE',
                credentials: 'include'
            });

            const data = await response.json();

            if (data.success) {
                // ✅ ATUALIZAÇÃO: Remover dos dados locais
                this.instituicoesData = this.instituicoesData.filter(inst => inst.id !== instituicaoId);
                
                // ✅ ATUALIZAÇÃO: Recarregar a aba atual
                this.recarregarAbaAtual();
                
                // ✅ ATUALIZAÇÃO: Atualizar contadores
                this.atualizarContadoresTabs();
                
                this.mostrarNotificacao(`Instituição "${nomeInstituicao}" eliminada com sucesso!`, 'success');
            } else {
                throw new Error(data.error);
            }
        } catch (error) {
            console.error('Erro ao eliminar instituição:', error);
            this.mostrarNotificacao('Erro ao eliminar instituição: ' + error.message, 'error');
        }
    }

    /**
     * Sai do painel administrativo
     */
    async sairPainelAdmin() {
        try {
            // Fazer logout
            await fetch('/api/auth/logout', { method: 'POST' });
            
            // Fechar modal
            const modal = document.querySelector('.modal-overlay');
            if (modal) {
                modal.remove();
            }
            
            // Mostrar tela de login principal
            const loginSection = document.getElementById('loginSection');
            if (loginSection) loginSection.style.display = 'block';
        } catch (error) {
            console.error('Erro ao sair do painel admin:', error);
        }
    }

    /**
     * Utilitários para erros do login admin
     */
    mostrarErroAdmin(mensagem) {
        const errorDiv = document.getElementById('adminLoginErrors');
        if (errorDiv) {
            errorDiv.innerHTML = `
                <div class="alert alert-error">
                    ${mensagem}
                </div>
            `;
            errorDiv.style.display = 'block';
        }
    }

    limparErrosAdmin() {
        const errorDiv = document.getElementById('adminLoginErrors');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    /**
     * Mostra o formulário de registro
     */
    mostrarFormularioRegistro() {
        // Esconde a tela de login ao abrir o registro
        const loginSection = document.getElementById('loginSection');
        if (loginSection) loginSection.style.display = 'none';

        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content registro-modal">
                <div class="modal-header">
                    <h3>📝 Registro de Nova Instituição</h3>
                    <p>Preencha os dados para solicitar acesso ao sistema</p>
                </div>
                
                <form id="formRegistro" class="registro-form">
                    <div class="form-grid">
                        <div class="form-group">
                            <label for="nome">Nome da Instituição *</label>
                            <input type="text" id="nome" name="nome" required>
                        </div>

                        <div class="form-group">
                            <label for="tipo_instituicao">Tipo de Instituição *</label>
                            <select id="tipo_instituicao" name="tipo_instituicao" required>
                                <option value="">Selecione o tipo</option>
                                ${this.tiposInstituicao.map(tipo => 
                                    `<option value="${tipo.valor}">${tipo.nome}</option>`
                                ).join('')}
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="username">Username *</label>
                            <input type="text" id="username" name="username" required>
                            <small class="form-help">Apenas letras, números e underscore</small>
                        </div>

                        <div class="form-group">
                            <label for="email">Email *</label>
                            <input type="email" id="email" name="email" required>
                        </div>

                        <div class="form-group">
                            <label for="password">Password *</label>
                            <input type="password" id="password" name="password" required>
                            <small class="form-help">Mínimo 6 caracteres</small>
                        </div>

                        <div class="form-group">
                            <label for="responsavel">Responsável *</label>
                            <input type="text" id="responsavel" name="responsavel" required>
                        </div>

                        <div class="form-group">
                            <label for="telefone">Telefone</label>
                            <input type="tel" id="telefone" name="telefone">
                        </div>

                        <div class="form-group">
                            <label for="documento_legal">Documento Legal</label>
                            <input type="text" id="documento_legal" name="documento_legal">
                            <small class="form-help">CNPJ, Registro, etc.</small>
                        </div>

                        <div class="form-group full-width">
                            <label for="endereco">Endereço</label>
                            <textarea id="endereco" name="endereco" rows="2"></textarea>
                        </div>

                        <div class="form-group full-width">
                            <label for="descricao">Descrição da Instituição</label>
                            <textarea id="descricao" name="descricao" rows="3"></textarea>
                        </div>
                    </div>

                    <div class="form-errors" id="formErrors" style="display: none;"></div>

                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" onclick="sistemaRegistro.fecharModalRegistro(this)">
                            Cancelar
                        </button>
                        <button type="submit" class="btn btn-primary">
                            📝 Registrar Instituição
                        </button>
                    </div>
                </form>
            </div>
        `;

        // Adicionar eventos
        const form = modal.querySelector('#formRegistro');
        form.addEventListener('submit', (e) => this.submeterRegistro(e));

        // Validação em tempo real
        const usernameInput = modal.querySelector('#username');
        const emailInput = modal.querySelector('#email');
        
        usernameInput.addEventListener('blur', () => this.verificarDisponibilidade('username', usernameInput.value));
        emailInput.addEventListener('blur', () => this.verificarDisponibilidade('email', emailInput.value));

        document.body.appendChild(modal);
    }

    /**
     * Fecha o modal de registro e mostra a tela de login novamente
     */
    fecharModalRegistro(botao) {
        // Remove o modal
        botao.closest('.modal-overlay').remove();
        // Mostra a tela de login novamente
        const loginSection = document.getElementById('loginSection');
        if (loginSection) loginSection.style.display = 'block';
    }

    /**
     * Verifica se username/email estão disponíveis
     */
    async verificarDisponibilidade(campo, valor) {
        if (!valor.trim()) return;

        try {
            const response = await fetch('/api/auth/verificar-disponibilidade', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ [campo]: valor })
            });

            const data = await response.json();
            const input = document.getElementById(campo);
            
            if (!data.disponivel) {
                input.classList.add('input-error');
                this.mostrarErroInput(input, `${campo === 'username' ? 'Username' : 'Email'} já está em uso`);
            } else {
                input.classList.remove('input-error');
                this.removerErroInput(input);
            }
        } catch (error) {
            console.error('Erro ao verificar disponibilidade:', error);
        }
    }

    /**
     * Submete o formulário de registro
     */
    async submeterRegistro(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        const dados = Object.fromEntries(formData.entries());

        // Limpar erros anteriores
        this.limparErros();

        try {
            const response = await fetch('/api/auth/registro', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(dados)
            });

            const data = await response.json();

            if (data.success) {
                // Fechar modal
                form.closest('.modal-overlay').remove();
                
                // Mostrar sucesso
                this.mostrarMensagemSucesso(
                    'Registro realizado com sucesso!',
                    'Sua instituição foi registrada e está aguardando aprovação. Você receberá uma notificação quando for aprovada.'
                );
            } else {
                this.mostrarErros([data.error]);
            }
        } catch (error) {
            console.error('Erro ao registrar:', error);
            this.mostrarErros(['Erro interno. Tente novamente.']);
        }
    }

    /**
     * Utilitários de interface
     */
    mostrarErros(erros) {
        const errorDiv = document.getElementById('formErrors');
        if (errorDiv) {
            errorDiv.innerHTML = `
                <div class="alert alert-error">
                    <ul>
                        ${erros.map(erro => `<li>${erro}</li>`).join('')}
                    </ul>
                </div>
            `;
            errorDiv.style.display = 'block';
        }
    }

    limparErros() {
        const errorDiv = document.getElementById('formErrors');
        if (errorDiv) {
            errorDiv.style.display = 'none';
        }
    }

    mostrarErroInput(input, mensagem) {
        let errorSpan = input.parentNode.querySelector('.input-error-message');
        if (!errorSpan) {
            errorSpan = document.createElement('span');
            errorSpan.className = 'input-error-message';
            input.parentNode.appendChild(errorSpan);
        }
        errorSpan.textContent = mensagem;
    }

    removerErroInput(input) {
        const errorSpan = input.parentNode.querySelector('.input-error-message');
        if (errorSpan) {
            errorSpan.remove();
        }
    }

    mostrarMensagemSucesso(titulo, mensagem) {
        const modal = document.createElement('div');
        modal.className = 'modal-overlay';
        modal.innerHTML = `
            <div class="modal-content sucesso-modal">
                <div class="modal-header">
                    <h3>✅ ${titulo}</h3>
                </div>
                <div class="modal-body">
                    <p>${mensagem}</p>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-primary" onclick="sistemaRegistro.fecharModalRegistro(this)">
                        OK
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }

    mostrarNotificacao(mensagem, tipo = 'info') {
        // Reutilizar sistema de notificações dos alertas
        if (window.sistemaAlertas) {
            window.sistemaAlertas.mostrarNotificacao(mensagem, tipo);
        } else {
            alert(mensagem);
        }
    }
}

// Instância global
const sistemaRegistro = new SistemaRegistro();

const registroCSS = `
<style>
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background: rgba(255, 255, 255, 0.98);
    backdrop-filter: blur(20px);
    border-radius: 25px;
    padding: 45px;
    border: 2px solid rgba(255, 255, 255, 0.5);
    box-shadow: 0 25px 50px rgba(17, 153, 142, 0.4);
    max-width: 90%;
    max-height: 90vh;
    overflow-y: auto;
}

.registro-modal, .admin-modal {
    max-width: 800px;
    max-height: 90vh;
    overflow-y: auto;
}

.admin-login-modal {
    max-width: 400px;
}

.registro-form, .admin-login-form {
    padding: 20px 0;
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
}

.form-group {
    display: flex;
    flex-direction: column;
}

.form-group.full-width {
    grid-column: 1 / -1;
}

.form-group label {
    font-weight: bold;
    margin-bottom: 5px;
    color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #4CAF50;
    box-shadow: 0 0 5px rgba(76, 175, 80, 0.3);
}

.form-help {
    font-size: 12px;
    color: #666;
    margin-top: 3px;
}

.input-error {
    border-color: #f44336 !important;
    box-shadow: 0 0 5px rgba(244, 67, 54, 0.3) !important;
}

.input-error-message {
    color: #f44336;
    font-size: 12px;
    margin-top: 3px;
}

.form-errors {
    margin: 15px 0;
}

.alert {
    padding: 15px;
    border-radius: 6px;
    margin: 10px 0;
}

.alert-error {
    background: #ffebee;
    border: 1px solid #ffcdd2;
    color: #c62828;
}

.alert ul {
    margin: 0;
    padding-left: 20px;
}

/* Estilos para gestão de instituições */
.tabs {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    border-bottom: 2px solid #e8f5e8;
    padding-bottom: 10px;
}

.tab-button {
    background: transparent;
    border: 2px solid #e8f5e8;
    padding: 10px 20px;
    border-radius: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    color: #5a7c76;
    font-weight: 600;
}

.tab-button:hover {
    border-color: #11998e;
    color: #11998e;
}

.tab-button.active {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    border-color: #11998e;
    color: white;
}

.instituicoes-lista {
    max-height: 500px;
    overflow-y: auto;
}

.instituicao-status {
    display: flex;
    align-items: center;
    gap: 10px;
}

.status-badge {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
}

.status-pendente {
    background: #fff3cd;
    color: #856404;
    border: 1px solid #ffeaa7;
}

.status-aprovada {
    background: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}

.status-rejeitada {
    background: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

.badge-protected {
    background: #e9ecef;
    color: #6c757d;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

.instituicao-card {
    border: 1px solid #e8f5e8;
    border-radius: 15px;
    padding: 20px;
    margin-bottom: 15px;
    background: white;
    transition: all 0.3s ease;
}

.instituicao-card:hover {
    box-shadow: 0 5px 15px rgba(17, 153, 142, 0.1);
    transform: translateY(-2px);
}

.instituicao-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #f0f0f0;
}

.instituicao-header h4 {
    margin: 0;
    color: #2d5a27;
    flex: 1;
}

.instituicao-details {
    margin-bottom: 15px;
}

.instituicao-details p {
    margin: 5px 0;
    font-size: 14px;
    color: #5a7c76;
}

.instituicao-details strong {
    color: #2d5a27;
}

.instituicao-actions {
    display: flex;
    gap: 10px;
    padding-top: 15px;
    border-top: 1px solid #f0f0f0;
}

.instituicoes-pendentes {
    max-height: 500px;
    overflow-y: auto;
}

.empty-state {
    text-align: center;
    padding: 40px;
    color: #666;
}

.sucesso-modal {
    max-width: 400px;
}

.modal-header {
    text-align: center;
    margin-bottom: 30px;
}

.modal-header h3 {
    color: #2d5a27;
    font-size: 1.8em;
    margin-bottom: 10px;
}

.modal-header p {
    color: #5a7c76;
    font-size: 1.1em;
}

.admin-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #eee;
}

.admin-info small {
    color: #666;
}

.modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #e0e0e0;
}

.btn {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 50px;
    font-size: 1em;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    text-decoration: none;
}

.btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 35px rgba(17, 153, 142, 0.6);
}

.btn-primary {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.btn-secondary {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.btn-success {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}

.btn-danger {
    background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
}

.btn-small {
    padding: 6px 12px;
    font-size: 0.8em;
}

@media (max-width: 768px) {
    .form-grid {
        grid-template-columns: 1fr;
    }
    
    .instituicao-actions {
        flex-direction: column;
    }
    
    .modal-content {
        padding: 25px;
        margin: 20px;
    }
    
    .modal-footer {
        flex-direction: column;
    }
    
    .admin-info {
        flex-direction: column;
        gap: 10px;
        text-align: center;
    }
    
    .tabs {
        flex-direction: column;
    }
    
    .instituicao-header {
        flex-direction: column;
        gap: 10px;
    }
    
    .instituicao-status {
        width: 100%;
        justify-content: space-between;
    }
}
</style>
`;

// Adicionar CSS ao documento
document.head.insertAdjacentHTML('beforeend', registroCSS);

// CSS para o sistema de registro (mantenha o mesmo CSS que você já tem)
// ... [O CSS permanece exatamente igual] ...