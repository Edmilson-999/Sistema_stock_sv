// Estado global da aplicação
let currentUser = null;
let currentSection = 'dashboard';

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    checkAuthStatus();
    loadInstitutions();
});

// Funções de autenticação
async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/check');
        const data = await response.json();
        
        if (data.authenticated) {
            currentUser = data.instituicao;
            showMainApp();
            loadDashboardStats();
        } else {
            showLoginSection();
        }
    } catch (error) {
        console.error('Erro ao verificar autenticação:', error);
        showLoginSection();
    }
}

async function loadInstitutions() {
    try {
        const response = await fetch('/api/auth/instituicoes');
        const data = await response.json();
        
        if (data.success) {
            const select = document.getElementById('institutionSelect');
            select.innerHTML = '<option value="">Selecione sua instituição</option>';
            
            data.instituicoes.forEach(inst => {
                const option = document.createElement('option');
                option.value = inst.username;
                option.textContent = inst.nome;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar instituições:', error);
    }
}

async function login() {
    const institution = document.getElementById('institutionSelect').value;
    const password = document.getElementById('accessCode').value;
    
    if (!institution) {
        showAlert('Por favor, escolha sua instituição.', 'danger', 'loginAlert');
        return;
    }
    
    if (!password) {
        showAlert('Por favor, digite o código de acesso.', 'danger', 'loginAlert');
        return;
    }
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: institution,
                password: password
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentUser = data.instituicao;
            showMainApp();
            loadDashboardStats();
            
            // Limpar campos
            document.getElementById('institutionSelect').value = '';
            document.getElementById('accessCode').value = '';
            hideAlert('loginAlert');
        } else {
            showAlert(data.error || 'Erro no login', 'danger', 'loginAlert');
        }
    } catch (error) {
        console.error('Erro no login:', error);
        showAlert('Erro de conexão. Tente novamente.', 'danger', 'loginAlert');
    }
}

async function logout() {
    try {
        await fetch('/api/auth/logout', { method: 'POST' });
        currentUser = null;
        showLoginSection();
    } catch (error) {
        console.error('Erro no logout:', error);
        // Mesmo com erro, fazer logout local
        currentUser = null;
        showLoginSection();
    }
}

// Funções de interface
function showLoginSection() {
    document.getElementById('loginSection').style.display = 'block';
    document.getElementById('mainApp').style.display = 'none';
}

function showMainApp() {
    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
    
    if (currentUser) {
        document.getElementById('institutionName').textContent = currentUser.nome;
    }
    
    // Mostrar apenas o dashboard inicialmente
    hideAllSections();
}

function hideAllSections() {
    document.getElementById('beneficiariosSection').classList.add('hidden');
    document.getElementById('stockSection').classList.add('hidden');
    document.getElementById('relatoriosSection').classList.add('hidden');
}

function showAlert(message, type = 'success', containerId = 'alertContainer') {
    const container = document.getElementById(containerId);
    
    if (containerId === 'alertContainer') {
        container.innerHTML = `
            <div class="alert alert-${type}">
                <span>${message}</span>
            </div>
        `;
        
        // Auto-hide após 5 segundos
        setTimeout(() => {
            container.innerHTML = '';
        }, 5000);
    } else {
        // Para alertas específicos (como loginAlert)
        const alertElement = document.getElementById(containerId);
        const messageElement = document.getElementById(containerId + 'Message');
        
        alertElement.className = `alert alert-${type}`;
        alertElement.classList.remove('hidden');
        messageElement.textContent = message;
    }
}

function hideAlert(alertId) {
    const alertElement = document.getElementById(alertId);
    if (alertElement) {
        alertElement.classList.add('hidden');
    }
}

// Funções do dashboard
async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();
        
        if (data.success) {
            const stats = data.stats;
            
            document.getElementById('statBeneficiarios').textContent = stats.sistema.total_beneficiarios;
            document.getElementById('statMovimentos').textContent = stats.instituicao.total_movimentos;
            document.getElementById('statEntradas').textContent = stats.instituicao.total_entradas;
            document.getElementById('statSaidas').textContent = stats.instituicao.total_saidas;
        }
    } catch (error) {
        console.error('Erro ao carregar estatísticas:', error);
    }
}

// Funções de navegação
function showBeneficiarios() {
    hideAllSections();
    document.getElementById('beneficiariosSection').classList.remove('hidden');
    currentSection = 'beneficiarios';
    loadBeneficiarios();
}

function showStock() {
    hideAllSections();
    document.getElementById('stockSection').classList.remove('hidden');
    currentSection = 'stock';
    loadMovimentosStock();
}

function showRelatorios() {
    hideAllSections();
    document.getElementById('relatoriosSection').classList.remove('hidden');
    currentSection = 'relatorios';
    loadRelatorios();
}

// Funções de beneficiários
async function loadBeneficiarios(search = '') {
    try {
        const url = search ? `/api/beneficiarios?search=${encodeURIComponent(search)}` : '/api/beneficiarios';
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.success) {
            displayBeneficiarios(data.beneficiarios);
        } else {
            document.getElementById('beneficiariosTable').innerHTML = 
                '<div class="alert alert-danger">Erro ao carregar beneficiários</div>';
        }
    } catch (error) {
        console.error('Erro ao carregar beneficiários:', error);
        document.getElementById('beneficiariosTable').innerHTML = 
            '<div class="alert alert-danger">Erro de conexão</div>';
    }
}

function displayBeneficiarios(beneficiarios) {
    const container = document.getElementById('beneficiariosTable');
    
    if (beneficiarios.length === 0) {
        container.innerHTML = '<div class="alert alert-warning">Nenhum beneficiário encontrado</div>';
        return;
    }
    
    let html = `
        <table class="table">
            <thead>
                <tr>
                    <th>NIF</th>
                    <th>Nome</th>
                    <th>Zona</th>
                    <th>Contacto</th>
                    <th>Ajudas Recebidas</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    beneficiarios.forEach(beneficiario => {
        html += `
            <tr>
                <td>${beneficiario.nif}</td>
                <td>${beneficiario.nome}</td>
                <td>${beneficiario.zona_residencia || '-'}</td>
                <td>${beneficiario.contacto || '-'}</td>
                <td><span class="badge badge-success">${beneficiario.total_ajudas}</span></td>
                <td>
                    <button class="btn btn-small" onclick="viewBeneficiario('${beneficiario.nif}')">👁️ Ver</button>
                </td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

async function searchBeneficiarios() {
    const search = document.getElementById('searchBeneficiarios').value;
    loadBeneficiarios(search);
}

async function viewBeneficiario(nif) {
    try {
        const response = await fetch(`/api/beneficiarios/${nif}`);
        const data = await response.json();
        
        if (data.success) {
            showBeneficiarioModal(data.beneficiario);
        } else {
            showAlert('Erro ao carregar beneficiário', 'danger');
        }
    } catch (error) {
        console.error('Erro ao carregar beneficiário:', error);
        showAlert('Erro de conexão', 'danger');
    }
}

function showBeneficiarioModal(beneficiario) {
    let historicoHtml = '';
    
    if (beneficiario.historico_ajuda && beneficiario.historico_ajuda.length > 0) {
        historicoHtml = `
            <h4 style="margin-top: 30px; margin-bottom: 15px; color: #2d5a27;">📋 Histórico de Ajuda</h4>
            <table class="table">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Item</th>
                        <th>Quantidade</th>
                        <th>Instituição</th>
                        <th>Motivo</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        beneficiario.historico_ajuda.forEach(ajuda => {
            const data = new Date(ajuda.data).toLocaleDateString('pt-PT');
            historicoHtml += `
                <tr>
                    <td>${data}</td>
                    <td>${ajuda.item_nome}</td>
                    <td>${ajuda.quantidade} ${ajuda.item_unidade}</td>
                    <td>${ajuda.instituicao_nome}</td>
                    <td>${ajuda.motivo || '-'}</td>
                </tr>
            `;
        });
        
        historicoHtml += '</tbody></table>';
    } else {
        historicoHtml = '<p style="margin-top: 20px; color: #5a7c76;">Ainda não recebeu ajuda registada no sistema.</p>';
    }
    
    const modalContent = `
        <h2 style="margin-bottom: 25px; color: #2d5a27;">👤 ${beneficiario.nome}</h2>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 25px;">
            <div>
                <strong>NIF:</strong> ${beneficiario.nif}<br>
                <strong>Idade:</strong> ${beneficiario.idade || 'Não informada'}<br>
                <strong>Contacto:</strong> ${beneficiario.contacto || 'Não informado'}
            </div>
            <div>
                <strong>Zona:</strong> ${beneficiario.zona_residencia || 'Não informada'}<br>
                <strong>Agregado:</strong> ${beneficiario.num_agregado || 'Não informado'} pessoas<br>
                <strong>Total de Ajudas:</strong> ${beneficiario.total_ajudas}
            </div>
        </div>
        
        ${beneficiario.necessidades ? `<p><strong>Necessidades:</strong> ${beneficiario.necessidades}</p>` : ''}
        ${beneficiario.perdas_pedidos ? `<p><strong>Perdas/Pedidos:</strong> ${beneficiario.perdas_pedidos}</p>` : ''}
        ${beneficiario.observacoes ? `<p><strong>Observações:</strong> ${beneficiario.observacoes}</p>` : ''}
        
        ${historicoHtml}
    `;
    
    document.getElementById('modalContent').innerHTML = modalContent;
    document.getElementById('genericModal').style.display = 'block';
}

// Funções de stock
async function loadMovimentosStock() {
    try {
        const response = await fetch('/api/stock/movimentos');
        const data = await response.json();
        
        if (data.success) {
            displayMovimentosStock(data.movimentos);
        } else {
            document.getElementById('stockContent').innerHTML = 
                '<div class="alert alert-danger">Erro ao carregar movimentos</div>';
        }
    } catch (error) {
        console.error('Erro ao carregar movimentos:', error);
        document.getElementById('stockContent').innerHTML = 
            '<div class="alert alert-danger">Erro de conexão</div>';
    }
}

function displayMovimentosStock(movimentos) {
    const container = document.getElementById('stockContent');
    
    if (movimentos.length === 0) {
        container.innerHTML = '<div class="alert alert-warning">Nenhum movimento registado</div>';
        return;
    }
    
    let html = `
        <h3 style="margin-bottom: 20px; color: #2d5a27;">📋 Últimos Movimentos</h3>
        <table class="table">
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Tipo</th>
                    <th>Item</th>
                    <th>Quantidade</th>
                    <th>Beneficiário</th>
                    <th>Motivo</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    movimentos.forEach(movimento => {
        const data = new Date(movimento.data).toLocaleDateString('pt-PT');
        const tipo = movimento.tipo_movimento === 'entrada' ? '⬆️ Entrada' : '⬇️ Saída';
        const badgeClass = movimento.tipo_movimento === 'entrada' ? 'badge-success' : 'badge-warning';
        
        html += `
            <tr>
                <td>${data}</td>
                <td><span class="badge ${badgeClass}">${tipo}</span></td>
                <td>${movimento.item_nome}</td>
                <td>${movimento.quantidade} ${movimento.item_unidade}</td>
                <td>${movimento.beneficiario_nome || '-'}</td>
                <td>${movimento.motivo || '-'}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

async function showRegistarEntrada() {
    try {
        const response = await fetch('/api/stock/itens');
        const data = await response.json();
        
        if (data.success) {
            showEntradaModal(data.itens);
        } else {
            showAlert('Erro ao carregar itens', 'danger');
        }
    } catch (error) {
        console.error('Erro ao carregar itens:', error);
        showAlert('Erro de conexão', 'danger');
    }
}

function showEntradaModal(itens) {
    let itensOptions = '<option value="">Selecione um item</option>';
    itens.forEach(item => {
        itensOptions += `<option value="${item.id}">${item.nome} (${item.unidade})</option>`;
    });
    
    const modalContent = `
        <h2 style="margin-bottom: 25px; color: #2d5a27;">⬆️ Registar Entrada de Stock</h2>
        
        <form id="entradaForm">
            <div class="form-group">
                <label>Item</label>
                <select id="entradaItem" required>
                    ${itensOptions}
                </select>
            </div>
            
            <div class="form-group">
                <label>Quantidade</label>
                <input type="number" id="entradaQuantidade" min="1" required>
            </div>
            
            <div class="form-group">
                <label>Origem da Doação</label>
                <input type="text" id="entradaOrigem" placeholder="Ex: Empresa X, Particular, etc.">
            </div>
            
            <div class="form-group">
                <label>Motivo</label>
                <textarea id="entradaMotivo" rows="3" placeholder="Descrição da entrada..."></textarea>
            </div>
            
            <div style="display: flex; gap: 15px; margin-top: 30px;">
                <button type="button" class="btn" onclick="registarEntrada()">✅ Registar Entrada</button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">❌ Cancelar</button>
            </div>
        </form>
    `;
    
    document.getElementById('modalContent').innerHTML = modalContent;
    document.getElementById('genericModal').style.display = 'block';
}

async function registarEntrada() {
    const itemId = document.getElementById('entradaItem').value;
    const quantidade = document.getElementById('entradaQuantidade').value;
    const origem = document.getElementById('entradaOrigem').value;
    const motivo = document.getElementById('entradaMotivo').value;
    
    if (!itemId || !quantidade) {
        showAlert('Item e quantidade são obrigatórios', 'danger');
        return;
    }
    
    try {
        const response = await fetch('/api/stock/entrada', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                item_id: parseInt(itemId),
                quantidade: parseInt(quantidade),
                origem_doacao: origem,
                motivo: motivo
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Entrada registada com sucesso!', 'success');
            closeModal();
            loadMovimentosStock();
            loadDashboardStats();
        } else {
            showAlert(data.error || 'Erro ao registar entrada', 'danger');
        }
    } catch (error) {
        console.error('Erro ao registar entrada:', error);
        showAlert('Erro de conexão', 'danger');
    }
}

async function showRegistarSaida() {
    try {
        const [itensResponse, beneficiariosResponse] = await Promise.all([
            fetch('/api/stock/itens'),
            fetch('/api/beneficiarios')
        ]);
        
        const itensData = await itensResponse.json();
        const beneficiariosData = await beneficiariosResponse.json();
        
        if (itensData.success && beneficiariosData.success) {
            showSaidaModal(itensData.itens, beneficiariosData.beneficiarios);
        } else {
            showAlert('Erro ao carregar dados', 'danger');
        }
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        showAlert('Erro de conexão', 'danger');
    }
}

function showSaidaModal(itens, beneficiarios) {
    let itensOptions = '<option value="">Selecione um item</option>';
    itens.forEach(item => {
        if (item.stock_total > 0) {
            itensOptions += `<option value="${item.id}">${item.nome} (${item.stock_total} ${item.unidade} disponíveis)</option>`;
        }
    });

    let beneficiariosOptions = '<option value="">Selecione um beneficiário</option>';
    // Corrigido: beneficiarios é um array, não um objeto com .beneficiarios
    beneficiarios.forEach(beneficiario => {
        beneficiariosOptions += `<option value="${beneficiario.nif}">${beneficiario.nome} (${beneficiario.nif})</option>`;
    });

    const modalContent = `
        <h2 style="margin-bottom: 25px; color: #2d5a27;">⬇️ Registar Saída de Stock</h2>
        <form id="saidaForm">
            <div class="form-group">
                <label>Item</label>
                <select id="saidaItem" required>
                    ${itensOptions}
                </select>
            </div>
            <div class="form-group">
                <label>Quantidade</label>
                <input type="number" id="saidaQuantidade" min="1" required>
            </div>
            <div class="form-group">
                <label>Beneficiário</label>
                <select id="saidaBeneficiario" required>
                    ${beneficiariosOptions}
                </select>
            </div>
            <div class="form-group">
                <label>Local de Entrega</label>
                <input type="text" id="saidaLocal" placeholder="Ex: Casa do beneficiário, Centro de distribuição, etc.">
            </div>
            <div class="form-group">
                <label>Motivo</label>
                <textarea id="saidaMotivo" rows="3" placeholder="Descrição da entrega..."></textarea>
            </div>
            <div style="display: flex; gap: 15px; margin-top: 30px;">
                <button type="button" class="btn" onclick="registarSaida()">✅ Registar Saída</button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">❌ Cancelar</button>
            </div>
        </form>
    `;

    document.getElementById('modalContent').innerHTML = modalContent;
    document.getElementById('genericModal').style.display = 'block';
}

async function registarSaida() {
    const itemId = document.getElementById('saidaItem').value;
    const quantidade = document.getElementById('saidaQuantidade').value;
    const beneficiarioNif = document.getElementById('saidaBeneficiario').value;
    const local = document.getElementById('saidaLocal').value;
    const motivo = document.getElementById('saidaMotivo').value;
    
    if (!itemId || !quantidade || !beneficiarioNif) {
        showAlert('Item, quantidade e beneficiário são obrigatórios', 'danger');
        return;
    }
    
    try {
        const response = await fetch('/api/stock/saida', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                item_id: parseInt(itemId),
                quantidade: parseInt(quantidade),
                beneficiario_nif: beneficiarioNif,
                local_entrega: local,
                motivo: motivo
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Saída registada com sucesso!', 'success');
            closeModal();
            loadMovimentosStock();
            loadDashboardStats();
        } else {
            showAlert(data.error || 'Erro ao registar saída', 'danger');
        }
    } catch (error) {
        console.error('Erro ao registar saída:', error);
        showAlert('Erro de conexão', 'danger');
    }
}

async function showResumoStock() {
    try {
        const response = await fetch('/api/stock/resumo');
        const data = await response.json();
        
        if (data.success) {
            displayResumoStock(data.resumo);
        } else {
            showAlert('Erro ao carregar resumo', 'danger');
        }
    } catch (error) {
        console.error('Erro ao carregar resumo:', error);
        showAlert('Erro de conexão', 'danger');
    }
}

function displayResumoStock(resumo) {
    const container = document.getElementById('stockContent');
    
    let html = `
        <h3 style="margin-bottom: 20px; color: #2d5a27;">📊 Resumo do Stock</h3>
        
        <div class="stats" style="margin-bottom: 30px;">
            <div class="stat-card">
                <div class="stat-number">${resumo.estatisticas.total_entradas}</div>
                <div class="stat-label">Total Entradas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${resumo.estatisticas.total_saidas}</div>
                <div class="stat-label">Total Saídas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${resumo.estatisticas.total_movimentos}</div>
                <div class="stat-label">Total Movimentos</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${resumo.estatisticas.movimentos_recentes}</div>
                <div class="stat-label">Últimos 7 dias</div>
            </div>
        </div>
    `;
    
    if (resumo.itens.length > 0) {
        html += `
            <h4 style="margin-bottom: 15px; color: #2d5a27;">📦 Itens com Movimento</h4>
            <table class="table">
                <thead>
                    <tr>
                        <th>Item</th>
                        <th>Categoria</th>
                        <th>Stock Total</th>
                        <th>Entradas (Instituição)</th>
                        <th>Saídas (Instituição)</th>
                    </tr>
                </thead>
                <tbody>
        `;
        
        resumo.itens.forEach(itemData => {
            const item = itemData.item;
            html += `
                <tr>
                    <td>${item.nome}</td>
                    <td>${item.categoria || '-'}</td>
                    <td><span class="badge badge-success">${itemData.stock_total} ${item.unidade}</span></td>
                    <td>${itemData.entradas_instituicao} ${item.unidade}</td>
                    <td>${itemData.saidas_instituicao} ${item.unidade}</td>
                </tr>
            `;
        });
        
        html += '</tbody></table>';
    } else {
        html += '<div class="alert alert-warning">Nenhum movimento de stock registado</div>';
    }
    
    container.innerHTML = html;
}

// Funções de relatórios
async function loadRelatorios() {
    try {
        const response = await fetch('/api/dashboard/atividade-recente?limit=20');
        const data = await response.json();
        
        if (data.success) {
            displayRelatorios(data.atividades);
        } else {
            document.getElementById('relatoriosContent').innerHTML = 
                '<div class="alert alert-danger">Erro ao carregar relatórios</div>';
        }
    } catch (error) {
        console.error('Erro ao carregar relatórios:', error);
        document.getElementById('relatoriosContent').innerHTML = 
            '<div class="alert alert-danger">Erro de conexão</div>';
    }
}

function displayRelatorios(atividades) {
    const container = document.getElementById('relatoriosContent');
    
    if (atividades.length === 0) {
        container.innerHTML = '<div class="alert alert-warning">Nenhuma atividade registada</div>';
        return;
    }
    
    let html = `
        <h3 style="margin-bottom: 20px; color: #2d5a27;">📋 Atividade Recente da Instituição</h3>
        <table class="table">
            <thead>
                <tr>
                    <th>Data</th>
                    <th>Tipo</th>
                    <th>Item</th>
                    <th>Quantidade</th>
                    <th>Detalhes</th>
                </tr>
            </thead>
            <tbody>
    `;
    
    atividades.forEach(atividade => {
        const data = new Date(atividade.data).toLocaleDateString('pt-PT');
        const tipo = atividade.tipo === 'entrada' ? '⬆️ Entrada' : '⬇️ Saída';
        const badgeClass = atividade.tipo === 'entrada' ? 'badge-success' : 'badge-warning';
        
        let detalhes = '';
        if (atividade.tipo === 'saida' && atividade.beneficiario_nome) {
            detalhes = `Para: ${atividade.beneficiario_nome}`;
        } else if (atividade.tipo === 'entrada' && atividade.origem_doacao) {
            detalhes = `De: ${atividade.origem_doacao}`;
        }
        
        html += `
            <tr>
                <td>${data}</td>
                <td><span class="badge ${badgeClass}">${tipo}</span></td>
                <td>${atividade.item_nome}</td>
                <td>${atividade.quantidade} ${atividade.unidade}</td>
                <td>${detalhes}</td>
            </tr>
        `;
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

// Funções de modal
function closeModal() {
    document.getElementById('genericModal').style.display = 'none';
}

// Fechar modal ao clicar fora
window.onclick = function(event) {
    const modal = document.getElementById('genericModal');
    if (event.target === modal) {
        closeModal();
    }
}

// Função para adicionar novo beneficiário (placeholder)
function showAddBeneficiario() {
    const modalContent = `
        <h2 style="margin-bottom: 25px; color: #2d5a27;">➕ Novo Beneficiário</h2>
        
        <form id="beneficiarioForm">
            <div class="form-group">
                <label>NIF *</label>
                <input type="text" id="beneficiarioNif" required>
            </div>
            
            <div class="form-group">
                <label>Nome *</label>
                <input type="text" id="beneficiarioNome" required>
            </div>
            
            <div class="form-group">
                <label>Idade</label>
                <input type="number" id="beneficiarioIdade" min="0">
            </div>
            
            <div class="form-group">
                <label>Contacto</label>
                <input type="text" id="beneficiarioContacto">
            </div>
            
            <div class="form-group">
                <label>Zona de Residência</label>
                <input type="text" id="beneficiarioZona">
            </div>
            
            <div class="form-group">
                <label>Número do Agregado Familiar</label>
                <input type="number" id="beneficiarioAgregado" min="1">
            </div>
            
            <div class="form-group">
                <label>Necessidades</label>
                <textarea id="beneficiarioNecessidades" rows="3"></textarea>
            </div>
            
            <div class="form-group">
                <label>Observações</label>
                <textarea id="beneficiarioObservacoes" rows="3"></textarea>
            </div>
            
            <div style="display: flex; gap: 15px; margin-top: 30px;">
                <button type="button" class="btn" onclick="criarBeneficiario()">✅ Criar Beneficiário</button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">❌ Cancelar</button>
            </div>
        </form>
    `;
    
    document.getElementById('modalContent').innerHTML = modalContent;
    document.getElementById('genericModal').style.display = 'block';
}

async function criarBeneficiario() {
    const nif = document.getElementById('beneficiarioNif').value;
    const nome = document.getElementById('beneficiarioNome').value;
    
    if (!nif || !nome) {
        showAlert('NIF e nome são obrigatórios', 'danger');
        return;
    }
    
    const beneficiarioData = {
        nif: nif,
        nome: nome,
        idade: document.getElementById('beneficiarioIdade').value || null,
        contacto: document.getElementById('beneficiarioContacto').value,
        zona_residencia: document.getElementById('beneficiarioZona').value,
        num_agregado: document.getElementById('beneficiarioAgregado').value || null,
        necessidades: document.getElementById('beneficiarioNecessidades').value,
        observacoes: document.getElementById('beneficiarioObservacoes').value
    };
    
    try {
        const response = await fetch('/api/beneficiarios', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(beneficiarioData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Beneficiário criado com sucesso!', 'success');
            closeModal();
            loadBeneficiarios();
            loadDashboardStats();
        } else {
            showAlert(data.error || 'Erro ao criar beneficiário', 'danger');
        }
    } catch (error) {
        console.error('Erro ao criar beneficiário:', error);
        showAlert('Erro de conexão', 'danger');
    }
}
