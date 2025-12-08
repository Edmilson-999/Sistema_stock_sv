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

    setTimeout(adicionarBotaoRelatorios, 100);
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

// Função para o botão "Consultar Beneficiário"
function showConsultarBeneficiario() {
    const modalContent = `
        <h2 style="margin-bottom: 25px; color: #2d5a27;">🔍 Consultar Beneficiário</h2>
        
        <form id="consultaBeneficiarioForm">
            <div class="form-group">
                <label>NIF do Beneficiário *</label>
                <input type="text" id="consultaNif" required placeholder="Digite o NIF do beneficiário">
            </div>
            
            <div style="display: flex; gap: 15px; margin-top: 30px;">
                <button type="button" class="btn" onclick="consultarBeneficiarioPorNif()">
                    🔍 Consultar
                </button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">
                    ❌ Cancelar
                </button>
            </div>
        </form>
        
        <div id="resultadoConsulta" style="margin-top: 20px; display: none;"></div>
    `;
    
    document.getElementById('modalContent').innerHTML = modalContent;
    document.getElementById('genericModal').style.display = 'block';
}

// Função para consultar beneficiário por NIF
async function consultarBeneficiarioPorNif() {
    const nif = document.getElementById('consultaNif').value.trim();
    
    if (!nif) {
        showAlert('Por favor, digite o NIF do beneficiário', 'danger');
        return;
    }
    
    try {
        console.log('🔍 Consultando beneficiário com NIF:', nif);
        
        const response = await fetch(`/api/beneficiarios/consultar_beneficiario?nif=${encodeURIComponent(nif)}`);
        const data = await response.json();
        
        console.log('📊 Resposta da consulta:', data);
        
        const resultadoDiv = document.getElementById('resultadoConsulta');
        
        if (data.success) {
            const beneficiario = data.consulta.beneficiario;
            const totalAjudas = data.consulta.total_ajudas_instituicao_atual + data.consulta.total_ajudas_outras_instituicoes;
            
            resultadoDiv.innerHTML = `
                <div class="alert alert-success">
                    <h4>✅ Beneficiário Encontrado</h4>
                    <p><strong>Nome:</strong> ${beneficiario.nome}</p>
                    <p><strong>NIF:</strong> ${beneficiario.nif}</p>
                    <p><strong>Idade:</strong> ${beneficiario.idade || 'Não informada'}</p>
                    <p><strong>Zona:</strong> ${beneficiario.zona_residencia || 'Não informada'}</p>
                    <p><strong>Total de Ajudas:</strong> ${totalAjudas}</p>
                    <p><strong>Instituições que ajudaram:</strong> ${data.consulta.instituicoes_que_ajudaram.join(', ') || 'Nenhuma'}</p>
                </div>
                
                ${data.consulta.avisos && data.consulta.avisos.length > 0 ? `
                    <div class="alert alert-warning">
                        <h5>⚠️ Alertas:</h5>
                        <ul>
                            ${data.consulta.avisos.map(alerta => `<li>${alerta}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            `;
        } else {
            resultadoDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h4>❌ Beneficiário Não Encontrado</h4>
                    <p>${data.error || 'Nenhum beneficiário encontrado com este NIF'}</p>
                </div>
            `;
        }
        
        resultadoDiv.style.display = 'block';
        
    } catch (error) {
        console.error('❌ Erro na consulta:', error);
        showAlert('Erro de conexão na consulta', 'danger');
    }
}

// Função para o botão "Consulta Rápida"
function showConsultaRapida() {
    const modalContent = `
        <h2 style="margin-bottom: 25px; color: #2d5a27;">⚡ Consulta Rápida</h2>
        
        <form id="consultaRapidaForm">
            <div class="form-group">
                <label>Termo de Pesquisa *</label>
                <input type="text" id="consultaTermo" required placeholder="Digite nome, NIF, zona ou contacto">
                <small class="form-help">Pesquisa por nome, NIF, zona de residência ou contacto</small>
            </div>
            
            <div style="display: flex; gap: 15px; margin-top: 30px;">
                <button type="button" class="btn" onclick="executarConsultaRapida()">
                    ⚡ Consultar
                </button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()">
                    ❌ Cancelar
                </button>
            </div>
        </form>
        
        <div id="resultadoConsultaRapida" style="margin-top: 20px; display: none;"></div>
    `;
    
    document.getElementById('modalContent').innerHTML = modalContent;
    document.getElementById('genericModal').style.display = 'block';
}

// Função para executar consulta rápida
async function executarConsultaRapida() {
    const termo = document.getElementById('consultaTermo').value.trim();
    
    if (!termo) {
        showAlert('Por favor, digite um termo para pesquisa', 'danger');
        return;
    }
    
    try {
        console.log('⚡ Executando consulta rápida com termo:', termo);
        
        const response = await fetch(`/api/beneficiarios/consulta_rapida?search=${encodeURIComponent(termo)}`);
        const data = await response.json();
        
        console.log('📊 Resposta da consulta rápida:', data);
        
        const resultadoDiv = document.getElementById('resultadoConsultaRapida');
        
        if (data.success && data.resultados && data.resultados.length > 0) {
            let resultadosHtml = `
                <div class="alert alert-success">
                    <h4>✅ ${data.total_encontrado} Beneficiário(s) Encontrado(s)</h4>
                </div>
                
                <div class="resultados-lista" style="max-height: 300px; overflow-y: auto;">
            `;
            
            data.resultados.forEach(beneficiario => {
                resultadosHtml += `
                    <div class="beneficiario-item" style="border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 8px;">
                        <p><strong>Nome:</strong> ${beneficiario.nome}</p>
                        <p><strong>NIF:</strong> ${beneficiario.nif}</p>
                        <p><strong>Contacto:</strong> ${beneficiario.contacto || 'Não informado'}</p>
                        <p><strong>Zona:</strong> ${beneficiario.zona_residencia || 'Não informada'}</p>
                        <p><strong>Total de Ajudas:</strong> ${beneficiario.total_ajudas || 0}</p>
                        <button class="btn btn-small" onclick="viewBeneficiario('${beneficiario.nif}')">
                            👁️ Ver Detalhes
                        </button>
                    </div>
                `;
            });
            
            resultadosHtml += '</div>';
            resultadoDiv.innerHTML = resultadosHtml;
        } else {
            resultadoDiv.innerHTML = `
                <div class="alert alert-warning">
                    <h4>⚠️ Nenhum Resultado</h4>
                    <p>Nenhum beneficiário encontrado com o termo "${termo}"</p>
                </div>
            `;
        }
        
        resultadoDiv.style.display = 'block';
        
    } catch (error) {
        console.error('❌ Erro na consulta rápida:', error);
        showAlert('Erro de conexão na consulta rápida', 'danger');
    }
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
        console.log("🔄 A carregar itens para entrada...");
        const response = await fetch('/api/stock/itens');
        const data = await response.json();
        
        console.log("Resposta da API /api/stock/itens:", data);

        // CORREÇÃO: Verificar múltiplas possibilidades de estrutura
        const itens = data.itens || data.data || [];

        if (itens.length > 0) {
            showEntradaModal(itens);
        } else {
            console.error("Erro: Itens não carregados ou array vazio", data);
            showAlert('Nenhum item disponível. É necessário criar itens primeiro.', 'warning');
        }
    } catch (error) {
        console.error('Erro ao carregar itens:', error);
        showAlert('Erro de conexão ao carregar itens', 'danger');
    }
}

function showEntradaModal(itens) {
    console.log("Itens recebidos para entrada:", itens);
    
    let itensOptions = '<option value="">Selecione um item</option>';
    
    if (Array.isArray(itens) && itens.length > 0) {
        itens.forEach(item => {
            // CORREÇÃO: Verificar múltiplas possibilidades de estrutura
            const itemId = item.id || item.item_id;
            const itemNome = item.nome || item.item_nome;
            const itemUnidade = item.unidade || item.item_unidade || 'unidade';

            if (itemId && itemNome) {
                itensOptions += `<option value="${itemId}">${itemNome} (${itemUnidade})</option>`;
            }
        });
    } else {
        itensOptions += '<option value="" disabled>Nenhum item disponível</option>';
    }

    const modalContent = `
        <h2 style="margin-bottom: 25px; color: #2d5a27;">⬆️ Registar Entrada de Stock</h2>
        
        <form id="entradaForm">
            <div class="form-group">
                <label>Item *</label>
                <select id="entradaItem" required style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; background: white;">
                    ${itensOptions}
                </select>
            </div>
            
            <div class="form-group">
                <label>Quantidade *</label>
                <input type="number" id="entradaQuantidade" min="1" required style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px;">
            </div>
            
            <div class="form-group">
                <label>Origem da Doação</label>
                <input type="text" id="entradaOrigem" placeholder="Ex: Empresa X, Particular, etc." style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px;">
            </div>
            
            <div class="form-group">
                <label>Motivo</label>
                <textarea id="entradaMotivo" rows="3" placeholder="Descrição da entrada..." style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px;"></textarea>
            </div>
            
            <div style="display: flex; gap: 15px; margin-top: 30px;">
                <button type="button" class="btn" onclick="registarEntrada()" style="flex: 1; padding: 15px; font-size: 16px;">✅ Registar Entrada</button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()" style="flex: 1; padding: 15px; font-size: 16px;">❌ Cancelar</button>
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
        console.log("🔄 A carregar dados para saída...");
        
        const [itensResponse, beneficiariosResponse] = await Promise.all([
            fetch('/api/stock/itens'),
            fetch('/api/beneficiarios')
        ]);
        
        const itensData = await itensResponse.json();
        const beneficiariosData = await beneficiariosResponse.json();
        
        console.log("Dados dos itens:", itensData);
        console.log("Dados dos beneficiários:", beneficiariosData);

        // CORREÇÃO: Verificar a estrutura real da resposta
        const itens = itensData.itens || itensData.data || [];
        const beneficiarios = beneficiariosData.beneficiarios || beneficiariosData.data || [];

        if (itens.length > 0 && beneficiarios.length > 0) {
            showSaidaModal(itens, beneficiarios);
        } else {
            let errorMsg = 'Erro ao carregar dados: ';
            if (itens.length === 0) errorMsg += 'Nenhum item disponível. ';
            if (beneficiarios.length === 0) errorMsg += 'Nenhum beneficiário disponível.';
            showAlert(errorMsg, 'danger');
        }
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        showAlert('Erro de conexão ao carregar dados', 'danger');
    }
}

function showSaidaModal(itens, beneficiarios) {
    console.log("Itens para saída:", itens);
    
    let itensOptions = '<option value="">Selecione um item</option>';
    let beneficiariosOptions = '<option value="">Selecione um beneficiário</option>';

    if (Array.isArray(itens) && itens.length > 0) {
        itens.forEach(item => {
            const itemId = item.id;
            const itemNome = item.nome;
            const itemUnidade = item.unidade || 'unidade';
            
            // CORREÇÃO: Usar stock_instituicao se stock_total não estiver disponível
            const stockTotal = item.stock_total || item.stock_instituicao || 0;

            console.log(`Item: ${itemNome}, Stock Total: ${item.stock_total}, Stock Instituição: ${item.stock_instituicao}, Stock Final: ${stockTotal}`);

            if (itemId && itemNome) {
                // Mostrar todos os itens, mas destacar os sem stock
                const disabled = stockTotal <= 0 ? 'disabled' : '';
                const stockStyle = stockTotal <= 0 ? 'color: #999; font-style: italic;' : 'color: #2d5a27;';
                const stockText = stockTotal > 0 ? `${stockTotal} ${itemUnidade} disponíveis` : 'SEM STOCK';
                
                itensOptions += `
                    <option value="${itemId}" ${disabled} style="${stockStyle}">
                        ${itemNome} (${stockText})
                    </option>
                `;
            }
        });
    }

    if (Array.isArray(beneficiarios) && beneficiarios.length > 0) {
        beneficiarios.forEach(beneficiario => {
            const nif = beneficiario.nif;
            const nome = beneficiario.nome;

            if (nif && nome) {
                beneficiariosOptions += `<option value="${nif}">${nome} (${nif})</option>`;
            }
        });
    }

    const modalContent = `
        <h2 style="margin-bottom: 25px; color: #2d5a27;">⬇️ Registar Saída de Stock</h2>
        
        <div style="margin-bottom: 20px; padding: 15px; background: #e8f5e8; border-radius: 8px; border-left: 4px solid #28a745;">
            <strong>💡 Informação:</strong> 
            <br>• Itens em <span style="color: #2d5a27;">verde</span> têm stock disponível
            <br>• Itens em <span style="color: #999;">cinza</span> estão sem stock
            <br>• Para usar itens sem stock, registe entradas primeiro
        </div>
        
        <form id="saidaForm">
            <div class="form-group">
                <label>Item *</label>
                <select id="saidaItem" required style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; background: white;">
                    ${itensOptions}
                </select>
            </div>
            
            <div class="form-group">
                <label>Quantidade *</label>
                <input type="number" id="saidaQuantidade" min="1" required style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px;">
            </div>
            
            <div class="form-group">
                <label>Beneficiário *</label>
                <select id="saidaBeneficiario" required style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px; background: white;">
                    ${beneficiariosOptions}
                </select>
            </div>
            
            <div class="form-group">
                <label>Local de Entrega</label>
                <input type="text" id="saidaLocal" placeholder="Ex: Casa do beneficiário, Centro de distribuição, etc." style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px;">
            </div>
            
            <div class="form-group">
                <label>Motivo</label>
                <textarea id="saidaMotivo" rows="3" placeholder="Descrição da entrega..." style="width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 8px; font-size: 16px;"></textarea>
            </div>
            
            <div style="display: flex; gap: 15px; margin-top: 30px;">
                <button type="button" class="btn" onclick="registarSaida()" style="flex: 1; padding: 15px; font-size: 16px;">✅ Registar Saída</button>
                <button type="button" class="btn" onclick="showRegistarEntrada()" style="flex: 1; padding: 15px; font-size: 16px;">📥 Registrar Entrada</button>
                <button type="button" class="btn btn-secondary" onclick="closeModal()" style="flex: 1; padding: 15px; font-size: 16px;">❌ Cancelar</button>
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


// ==================== ADICIONAR CSS DINAMICAMENTE ====================

function adicionarCSSRelatorios() {
    // Verificar se o CSS já foi adicionado
    if (document.getElementById('css-relatorios')) {
        return;
    }
    
    const css = `
    /* Estilos para o sistema de relatórios */
    .relatorios-interface {
        max-width: 900px;
        max-height: 80vh;
        overflow-y: auto;
    }
    
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
    
    .relatorio-card {
        border: 1px solid #e8f5e8;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        background: white;
        transition: all 0.3s ease;
    }
    
    .relatorio-card:hover {
        box-shadow: 0 5px 15px rgba(17, 153, 142, 0.1);
        transform: translateY(-2px);
    }
    
    .periodo-card {
        border: 1px solid #e8f5e8;
        border-radius: 10px;
        padding: 15px;
        background: white;
        transition: all 0.3s ease;
    }
    
    .periodo-card:hover {
        box-shadow: 0 5px 15px rgba(17, 153, 142, 0.1);
        transform: translateY(-2px);
        border-color: #11998e;
    }
    
    .stat-card-small {
        background: white;
        border: 1px solid #e8f5e8;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    
    .stat-card-small .stat-number {
        font-size: 24px;
        font-weight: bold;
        color: #2d5a27;
        margin-bottom: 5px;
    }
    
    .stat-card-small .stat-label {
        font-size: 14px;
        color: #5a7c76;
    }
    
    .gerar-relatorio-form {
        max-width: 500px;
        margin: 0 auto;
    }
    
    .form-check {
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .form-check input {
        width: auto;
    }
    
    .impressao-relatorio {
        background: white;
        padding: 30px;
        border-radius: 10px;
        max-width: 800px;
        margin: 0 auto;
    }
    
    @media print {
        .impressao-relatorio {
            box-shadow: none;
            border: none;
            padding: 0;
        }
        
        .no-print {
            display: none !important;
        }
    }
    `;
    
    const style = document.createElement('style');
    style.id = 'css-relatorios';
    style.textContent = css;
    document.head.appendChild(style);
    
    console.log('✅ CSS para relatórios adicionado');
}

// Chamar a função quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(adicionarCSSRelatorios, 1000);
});

// ==================== SISTEMA DE RELATÓRIOS ====================

// Função para mostrar a interface de relatórios
function showRelatoriosInterface() {
    // Garantir que o CSS está carregado
    adicionarCSSRelatorios();
    const modalContent = `
        <div class="relatorios-interface">
            <h2 style="margin-bottom: 25px; color: #2d5a27;">📊 Sistema de Relatórios Mensais</h2>
            
            <div class="tabs" style="margin-bottom: 20px;">
                <button class="tab-button active" onclick="mostrarAbaRelatorios('gerar')">
                    📅 Gerar Novo
                </button>
                <button class="tab-button" onclick="mostrarAbaRelatorios('listar')">
                    📋 Relatórios Salvos
                </button>
                <button class="tab-button" onclick="mostrarAbaRelatorios('periodos')">
                    📅 Períodos Disponíveis
                </button>
            </div>
            
            <div id="abaRelatoriosConteudo">
                <!-- Conteúdo será carregado aqui -->
            </div>
        </div>
    `;
    
    document.getElementById('modalContent').innerHTML = modalContent;
    document.getElementById('genericModal').style.display = 'block';
    
    // Carregar aba inicial
    mostrarAbaRelatorios('gerar');
}

// Função para alternar abas
function mostrarAbaRelatorios(aba) {
    document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    const conteudo = document.getElementById('abaRelatoriosConteudo');
    
    switch(aba) {
        case 'gerar':
            carregarInterfaceGerarRelatorio();
            break;
        case 'listar':
            carregarRelatoriosSalvos();
            break;
        case 'periodos':
            carregarPeriodosDisponiveis();
            break;
    }
}

// Interface para gerar novo relatório
async function carregarInterfaceGerarRelatorio() {
    const conteudo = document.getElementById('abaRelatoriosConteudo');
    const dataAtual = new Date();
    const anoAtual = dataAtual.getFullYear();
    const mesAtual = dataAtual.getMonth() + 1; // Janeiro = 1
    
    const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    let opcoesMes = '';
    for (let i = 0; i < meses.length; i++) {
        const selecionado = (i + 1) === mesAtual ? 'selected' : '';
        opcoesMes += `<option value="${i + 1}" ${selecionado}>${meses[i]}</option>`;
    }
    
    let opcoesAno = '';
    for (let ano = anoAtual; ano >= anoAtual - 5; ano--) {
        const selecionado = ano === anoAtual ? 'selected' : '';
        opcoesAno += `<option value="${ano}" ${selecionado}>${ano}</option>`;
    }
    
    conteudo.innerHTML = `
        <div class="gerar-relatorio-form">
            <h3 style="margin-bottom: 20px; color: #2d5a27;">📅 Gerar Relatório Mensal</h3>
            
            <form id="formGerarRelatorio">
                <div class="form-group">
                    <label>Mês</label>
                    <select id="relatorioMes" required>
                        ${opcoesMes}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Ano</label>
                    <select id="relatorioAno" required>
                        ${opcoesAno}
                    </select>
                </div>
                
                <div class="form-check" style="margin: 15px 0;">
                    <input type="checkbox" id="salvarRelatorio" checked>
                    <label for="salvarRelatorio">Salvar relatório no sistema</label>
                </div>
                
                <div style="display: flex; gap: 15px; margin-top: 25px;">
                    <button type="button" class="btn" onclick="gerarRelatorioMensal()">
                        📊 Gerar Relatório
                    </button>
                    <button type="button" class="btn btn-secondary" onclick="closeModal()">
                        ❌ Cancelar
                    </button>
                </div>
            </form>
            
            <div id="resultadoGeracao" style="margin-top: 20px; display: none;"></div>
        </div>
    `;
}

// Função para gerar relatório
async function gerarRelatorioMensal() {
    const mes = document.getElementById('relatorioMes').value;
    const ano = document.getElementById('relatorioAno').value;
    const salvar = document.getElementById('salvarRelatorio').checked;
    
    try {
        const response = await fetch('/api/relatorios/mensal/gerar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                ano: parseInt(ano),
                mes: parseInt(mes),
                salvar: salvar
            })
        });
        
        const data = await response.json();
        const resultadoDiv = document.getElementById('resultadoGeracao');
        
        if (data.success) {
            resultadoDiv.innerHTML = `
                <div class="alert alert-success">
                    <h4>✅ Relatório Gerado com Sucesso!</h4>
                    <p><strong>Período:</strong> ${mes}/${ano}</p>
                    <p><strong>Total de Movimentos:</strong> ${data.relatorio.resumo.total_movimentos}</p>
                    <p><strong>Entradas:</strong> ${data.relatorio.resumo.total_entradas}</p>
                    <p><strong>Saídas:</strong> ${data.relatorio.resumo.total_saidas}</p>
                    
                    <div style="margin-top: 20px;">
                        <button class="btn" onclick="visualizarRelatorio(${ano}, ${mes})">
                            👁️ Visualizar Relatório
                        </button>
                        <button class="btn" onclick="imprimirRelatorioGerado(${ano}, ${mes})">
                            🖨️ Imprimir
                        </button>
                    </div>
                </div>
            `;
        } else {
            resultadoDiv.innerHTML = `
                <div class="alert alert-danger">
                    <h4>❌ Erro ao Gerar Relatório</h4>
                    <p>${data.error || 'Erro desconhecido'}</p>
                </div>
            `;
        }
        
        resultadoDiv.style.display = 'block';
        
    } catch (error) {
        console.error('Erro ao gerar relatório:', error);
        showAlert('Erro de conexão ao gerar relatório', 'danger');
    }
}

// Função para visualizar relatório
async function visualizarRelatorio(ano, mes) {
    try {
        const response = await fetch(`/api/relatorios/mensal/por-mes/${ano}/${mes}`);
        const data = await response.json();
        
        if (data.success) {
            mostrarRelatorioDetalhado(data.relatorio, data.existe);
        } else {
            showAlert('Erro ao carregar relatório: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Erro ao visualizar relatório:', error);
        showAlert('Erro de conexão', 'danger');
    }
}

// Função para mostrar relatório detalhado
function mostrarRelatorioDetalhado(relatorio, existe) {
    const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    const mesNome = meses[relatorio.mes - 1] || `Mês ${relatorio.mes}`;
    
    let entradasHTML = '';
    if (relatorio.dados.entradas && relatorio.dados.entradas.lista.length > 0) {
        entradasHTML = `
            <h4 style="margin-top: 20px; margin-bottom: 10px; color: #2d5a27;">📥 Entradas do Mês (${relatorio.dados.entradas.lista.length})</h4>
            <table class="table">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Item</th>
                        <th>Quantidade</th>
                        <th>Origem</th>
                    </tr>
                </thead>
                <tbody>
                    ${relatorio.dados.entradas.lista.map(entrada => `
                        <tr>
                            <td>${entrada.data}</td>
                            <td>${entrada.item}</td>
                            <td>${entrada.quantidade} ${entrada.unidade}</td>
                            <td>${entrada.origem}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } else {
        entradasHTML = '<p>Nenhuma entrada registada neste mês.</p>';
    }
    
    let saidasHTML = '';
    if (relatorio.dados.saidas && relatorio.dados.saidas.lista.length > 0) {
        saidasHTML = `
            <h4 style="margin-top: 20px; margin-bottom: 10px; color: #2d5a27;">📤 Saídas do Mês (${relatorio.dados.saidas.lista.length})</h4>
            <table class="table">
                <thead>
                    <tr>
                        <th>Data</th>
                        <th>Item</th>
                        <th>Quantidade</th>
                        <th>Beneficiário</th>
                        <th>Observações</th>
                    </tr>
                </thead>
                <tbody>
                    ${relatorio.dados.saidas.lista.map(saida => `
                        <tr>
                            <td>${saida.data}</td>
                            <td>${saida.item}</td>
                            <td>${saida.quantidade} ${saida.unidade}</td>
                            <td>${saida.beneficiario}</td>
                            <td>${saida.observacoes || '-'}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } else {
        saidasHTML = '<p>Nenhuma saída registada neste mês.</p>';
    }
    
    const modalContent = `
        <div class="relatorio-detalhado">
            <h2 style="margin-bottom: 25px; color: #2d5a27;">
                📊 Relatório Mensal – ${mesNome}/${relatorio.ano}
                ${existe ? '<span class="badge badge-success" style="font-size: 0.7em; margin-left: 10px;">SALVO</span>' : ''}
            </h2>
            
            <div class="resumo-relatorio" style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 25px;">
                <h4>📈 Estatísticas do Mês</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px;">
                    <div class="stat-card-small">
                        <div class="stat-number">${relatorio.dados.resumo.total_movimentos}</div>
                        <div class="stat-label">Total de Movimentos</div>
                    </div>
                    <div class="stat-card-small">
                        <div class="stat-number">${relatorio.dados.resumo.total_entradas}</div>
                        <div class="stat-label">Entradas</div>
                    </div>
                    <div class="stat-card-small">
                        <div class="stat-number">${relatorio.dados.resumo.total_saidas}</div>
                        <div class="stat-label">Saídas</div>
                    </div>
                    <div class="stat-card-small">
                        <div class="stat-number">${relatorio.dados.resumo.beneficiarios_atendidos}</div>
                        <div class="stat-label">Beneficiários Atendidos</div>
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #ddd;">
                    <p><strong>Quantidade Total Entrada:</strong> ${relatorio.dados.resumo.quantidade_total_entradas}</p>
                    <p><strong>Quantidade Total Saída:</strong> ${relatorio.dados.resumo.quantidade_total_saidas}</p>
                    <p><strong>Saldo do Mês:</strong> <span class="${relatorio.dados.resumo.saldo_mensal >= 0 ? 'text-success' : 'text-danger'}">${relatorio.dados.resumo.saldo_mensal}</span></p>
                </div>
            </div>
            
            ${entradasHTML}
            ${saidasHTML}
            
            <div style="display: flex; gap: 15px; margin-top: 30px; flex-wrap: wrap;">
                <button class="btn" onclick="imprimirRelatorio(${relatorio.id})">
                    🖨️ Imprimir Relatório
                </button>
                <button class="btn btn-secondary" onclick="closeModal()">
                    ❌ Fechar
                </button>
            </div>
        </div>
    `;
    
    document.getElementById('modalContent').innerHTML = modalContent;
    document.getElementById('genericModal').style.display = 'block';
}

// Função para carregar relatórios salvos
async function carregarRelatoriosSalvos() {
    const conteudo = document.getElementById('abaRelatoriosConteudo');
    
    try {
        const response = await fetch('/api/relatorios/mensal/listar');
        const data = await response.json();
        
        if (data.success) {
            if (data.relatorios.length > 0) {
                let relatoriosHTML = `
                    <h3 style="margin-bottom: 20px; color: #2d5a27;">📋 Relatórios Salvos</h3>
                    <p>Total: ${data.relatorios.length} relatório(s) salvo(s)</p>
                    
                    <div class="relatorios-lista" style="max-height: 400px; overflow-y: auto; margin-top: 20px;">
                `;
                
                data.relatorios.forEach(relatorio => {
                    relatoriosHTML += `
                        <div class="relatorio-card" style="border: 1px solid #ddd; padding: 15px; margin-bottom: 10px; border-radius: 8px;">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <h4 style="margin: 0; color: #2d5a27;">${relatorio.mes_nome}/${relatorio.ano}</h4>
                                    <small>Gerado em: ${new Date(relatorio.data_geracao).toLocaleDateString('pt-PT')}</small>
                                </div>
                                <div style="text-align: right;">
                                    <span class="badge badge-success">${relatorio.movimentos_count} movimentos</span><br>
                                    <span class="badge badge-info">Entradas: ${relatorio.total_entradas}</span>
                                    <span class="badge badge-warning">Saídas: ${relatorio.total_saidas}</span>
                                </div>
                            </div>
                            
                            <div style="display: flex; gap: 10px; margin-top: 15px;">
                                <button class="btn btn-small" onclick="visualizarRelatorio(${relatorio.ano}, ${relatorio.mes})">
                                    👁️ Visualizar
                                </button>
                                <button class="btn btn-small" onclick="imprimirRelatorio(${relatorio.id})">
                                    🖨️ Imprimir
                                </button>
                                <button class="btn btn-small btn-secondary" onclick="gerarNovamenteRelatorio(${relatorio.ano}, ${relatorio.mes})">
                                    🔄 Regenerar
                                </button>
                            </div>
                        </div>
                    `;
                });
                
                relatoriosHTML += '</div>';
                conteudo.innerHTML = relatoriosHTML;
            } else {
                conteudo.innerHTML = `
                    <div class="alert alert-warning">
                        <h4>📭 Nenhum Relatório Salvo</h4>
                        <p>Não existem relatórios salvos no sistema.</p>
                        <p>Gere um novo relatório usando a aba "Gerar Novo".</p>
                    </div>
                `;
            }
        } else {
            conteudo.innerHTML = `
                <div class="alert alert-danger">
                    <h4>❌ Erro ao Carregar Relatórios</h4>
                    <p>${data.error || 'Erro desconhecido'}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar relatórios:', error);
        conteudo.innerHTML = `
            <div class="alert alert-danger">
                <h4>❌ Erro de Conexão</h4>
                <p>Não foi possível carregar os relatórios salvos.</p>
            </div>
        `;
    }
}

// Função para carregar períodos disponíveis
async function carregarPeriodosDisponiveis() {
    const conteudo = document.getElementById('abaRelatoriosConteudo');
    
    try {
        const response = await fetch('/api/relatorios/mensal/periodos-disponiveis');
        const data = await response.json();
        
        if (data.success) {
            if (data.periodos.length > 0) {
                let periodosHTML = `
                    <h3 style="margin-bottom: 20px; color: #2d5a27;">📅 Períodos com Dados Disponíveis</h3>
                    <p>Total: ${data.periodos.length} período(s) com movimentos registados</p>
                    
                    <div class="periodos-lista" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 15px; margin-top: 20px;">
                `;
                
                data.periodos.forEach(periodo => {
                    periodosHTML += `
                        <div class="periodo-card" style="border: 1px solid #ddd; padding: 15px; border-radius: 8px; text-align: center; cursor: pointer;" onclick="visualizarRelatorio(${periodo.ano}, ${periodo.mes})">
                            <div style="font-size: 2em; margin-bottom: 10px;">📅</div>
                            <h4 style="margin: 0; color: #2d5a27;">${periodo.mes_nome}/${periodo.ano}</h4>
                            <small>Clique para gerar relatório</small>
                        </div>
                    `;
                });
                
                periodosHTML += '</div>';
                conteudo.innerHTML = periodosHTML;
            } else {
                conteudo.innerHTML = `
                    <div class="alert alert-warning">
                        <h4>📭 Nenhum Dado Disponível</h4>
                        <p>Não existem movimentos registados no sistema.</p>
                        <p>Registe algumas entradas e saídas para poder gerar relatórios.</p>
                    </div>
                `;
            }
        } else {
            conteudo.innerHTML = `
                <div class="alert alert-danger">
                    <h4>❌ Erro ao Carregar Períodos</h4>
                    <p>${data.error || 'Erro desconhecido'}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Erro ao carregar períodos:', error);
        conteudo.innerHTML = `
            <div class="alert alert-danger">
                <h4>❌ Erro de Conexão</h4>
                <p>Não foi possível carregar os períodos disponíveis.</p>
            </div>
        `;
    }
}

// Função para imprimir relatório
async function imprimirRelatorio(relatorioId) {
    try {
        const response = await fetch(`/api/relatorios/mensal/${relatorioId}/imprimir`);
        const data = await response.json();
        
        if (data.success) {
            mostrarRelatorioParaImpressao(data.para_impressao);
        } else {
            showAlert('Erro ao preparar impressão: ' + data.error, 'danger');
        }
    } catch (error) {
        console.error('Erro ao imprimir relatório:', error);
        showAlert('Erro de conexão', 'danger');
    }
}

// Função para mostrar relatório formatado para impressão
function mostrarRelatorioParaImpressao(relatorio) {
    const meses = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    
    // Formatar conteúdo para impressão
    const conteudoImpressao = `
        <div class="impressao-relatorio" style="font-family: Arial, sans-serif;">
            <style>
                @media print {
                    body * { visibility: hidden; }
                    .impressao-relatorio, .impressao-relatorio * { visibility: visible; }
                    .impressao-relatorio { position: absolute; left: 0; top: 0; width: 100%; }
                    .no-print { display: none !important; }
                }
                .impressao-relatorio {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: white;
                }
                .cabecalho-impressao {
                    text-align: center;
                    border-bottom: 3px solid #2d5a27;
                    padding-bottom: 20px;
                    margin-bottom: 30px;
                }
                .secao {
                    margin-bottom: 30px;
                    page-break-inside: avoid;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin: 10px 0;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f8f9fa;
                }
                .total {
                    font-weight: bold;
                    background-color: #f8f9fa;
                }
            </style>
            
            <div class="cabecalho-impressao">
                <h1 style="color: #2d5a27; margin-bottom: 5px;">${relatorio.cabecalho.titulo}</h1>
                <h3 style="color: #666; margin-bottom: 10px;">${relatorio.cabecalho.instituicao}</h3>
                <p><strong>Período:</strong> ${relatorio.cabecalho.periodo}</p>
                <p><strong>Data de Geração:</strong> ${relatorio.cabecalho.data_geracao}</p>
            </div>
            
            <div class="secao">
                <h2 style="color: #2d5a27; border-bottom: 2px solid #2d5a27; padding-bottom: 5px;">📈 RESUMO DO MÊS</h2>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; margin: 15px 0;">
                    <div style="text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                        <div style="font-size: 24px; font-weight: bold; color: #2d5a27;">${relatorio.resumo.total_movimentos}</div>
                        <div>Total de Movimentos</div>
                    </div>
                    <div style="text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                        <div style="font-size: 24px; font-weight: bold; color: #28a745;">${relatorio.resumo.total_entradas}</div>
                        <div>Entradas</div>
                    </div>
                    <div style="text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                        <div style="font-size: 24px; font-weight: bold; color: #dc3545;">${relatorio.resumo.total_saidas}</div>
                        <div>Saídas</div>
                    </div>
                    <div style="text-align: center; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
                        <div style="font-size: 24px; font-weight: bold; color: #2d5a27;">${relatorio.resumo.beneficiarios_atendidos}</div>
                        <div>Beneficiários Atendidos</div>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <p><strong>Quantidade Total Entrada:</strong> ${relatorio.resumo.quantidade_total_entradas}</p>
                    <p><strong>Quantidade Total Saída:</strong> ${relatorio.resumo.quantidade_total_saidas}</p>
                    <p><strong>Saldo do Mês:</strong> <span style="font-weight: bold; ${relatorio.resumo.saldo_mensal >= 0 ? 'color: #28a745;' : 'color: #dc3545;'}">${relatorio.resumo.saldo_mensal}</span></p>
                </div>
            </div>
            
            <div class="secao">
                <h2 style="color: #2d5a27; border-bottom: 2px solid #2d5a27; padding-bottom: 5px;">📥 ENTRADAS DO MÊS</h2>
                ${relatorio.entradas.lista.length > 0 ? `
                    <table>
                        <thead>
                            <tr>
                                <th>Data</th>
                                <th>Item</th>
                                <th>Quantidade</th>
                                <th>Origem</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${relatorio.entradas.lista.map(entrada => `
                                <tr>
                                    <td>${entrada.data}</td>
                                    <td>${entrada.item}</td>
                                    <td>${entrada.quantidade} ${entrada.unidade}</td>
                                    <td>${entrada.origem}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                ` : '<p style="text-align: center; color: #666; font-style: italic;">Nenhuma entrada registada neste mês.</p>'}
            </div>
            
            <div class="secao">
                <h2 style="color: #2d5a27; border-bottom: 2px solid #2d5a27; padding-bottom: 5px;">📤 SAÍDAS DO MÊS</h2>
                ${relatorio.saidas.lista.length > 0 ? `
                    <table>
                        <thead>
                            <tr>
                                <th>Data</th>
                                <th>Item</th>
                                <th>Quantidade</th>
                                <th>Beneficiário</th>
                                <th>Observações</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${relatorio.saidas.lista.map(saida => `
                                <tr>
                                    <td>${saida.data}</td>
                                    <td>${saida.item}</td>
                                    <td>${saida.quantidade} ${saida.unidade}</td>
                                    <td>${saida.beneficiario}</td>
                                    <td>${saida.observacoes || '-'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                ` : '<p style="text-align: center; color: #666; font-style: italic;">Nenhuma saída registada neste mês.</p>'}
            </div>
            
            <div class="secao no-print" style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 2px dashed #ddd;">
                <button class="btn" onclick="window.print()" style="padding: 10px 20px; font-size: 16px;">
                    🖨️ Imprimir Este Relatório
                </button>
                <button class="btn btn-secondary" onclick="closeModal()" style="padding: 10px 20px; font-size: 16px; margin-left: 10px;">
                    ❌ Fechar
                </button>
            </div>
        </div>
    `;
    
    document.getElementById('modalContent').innerHTML = conteudoImpressao;
    document.getElementById('genericModal').style.display = 'block';
}

// Função para gerar novamente um relatório
async function gerarNovamenteRelatorio(ano, mes) {
    if (confirm(`Deseja regenerar o relatório de ${mes}/${ano}?`)) {
        try {
            const response = await fetch('/api/relatorios/mensal/gerar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    ano: ano,
                    mes: mes,
                    salvar: true
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert('Relatório regenerado com sucesso!', 'success');
                // Recarregar a lista
                carregarRelatoriosSalvos();
            } else {
                showAlert('Erro ao regenerar relatório: ' + data.error, 'danger');
            }
        } catch (error) {
            console.error('Erro ao regenerar relatório:', error);
            showAlert('Erro de conexão', 'danger');
        }
    }
}

function adicionarBotaoRelatorios() {
    console.log('🔍 Procurando local para adicionar botão de relatórios...');
    
    // TENTATIVA 1: Procurar a seção de ações no stock
    const stockSection = document.getElementById('stockSection');
    if (stockSection) {
        // Encontrar ou criar a div de botões
        let actionButtons = stockSection.querySelector('.action-buttons');
        
        if (!actionButtons) {
            // Criar div de botões se não existir
            actionButtons = document.createElement('div');
            actionButtons.className = 'action-buttons';
            actionButtons.style.cssText = 'display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap;';
            
            // Inserir no início da seção
            stockSection.insertBefore(actionButtons, stockSection.firstChild);
        }
        
        // Verificar se o botão já existe
        if (!document.getElementById('botaoRelatorios')) {
            const botaoRelatorios = document.createElement('button');
            botaoRelatorios.id = 'botaoRelatorios';
            botaoRelatorios.className = 'btn';
            botaoRelatorios.innerHTML = '📊 Relatórios Mensais';
            botaoRelatorios.onclick = showRelatoriosInterface;
            actionButtons.appendChild(botaoRelatorios);
            
            console.log('✅ Botão de relatórios adicionado na seção Stock');
            return true;
        }
    }
    
    // TENTATIVA 2: Procurar em outras seções
    const sections = ['beneficiariosSection', 'relatoriosSection'];
    for (const sectionId of sections) {
        const section = document.getElementById(sectionId);
        if (section) {
            let actionButtons = section.querySelector('.action-buttons');
            if (!actionButtons) {
                actionButtons = document.createElement('div');
                actionButtons.className = 'action-buttons';
                actionButtons.style.cssText = 'display: flex; gap: 15px; margin-bottom: 30px; flex-wrap: wrap;';
                section.insertBefore(actionButtons, section.firstChild);
            }
            
            if (!document.getElementById('botaoRelatorios')) {
                const botaoRelatorios = document.createElement('button');
                botaoRelatorios.id = 'botaoRelatorios';
                botaoRelatorios.className = 'btn';
                botaoRelatorios.innerHTML = '📊 Relatórios Mensais';
                botaoRelatorios.onclick = showRelatoriosInterface;
                actionButtons.appendChild(botaoRelatorios);
                
                console.log(`✅ Botão de relatórios adicionado na seção ${sectionId}`);
                return true;
            }
        }
    }
    
    // TENTATIVA 3: Adicionar na barra de navegação principal
    const navBar = document.querySelector('.navbar-nav, nav, .navigation');
    if (navBar && !document.getElementById('botaoRelatorios')) {
        const botaoRelatorios = document.createElement('li');
        botaoRelatorios.id = 'botaoRelatorios';
        botaoRelatorios.innerHTML = `
            <a href="#" onclick="showRelatoriosInterface(); return false;" class="nav-link">
                📊 Relatórios
            </a>
        `;
        navBar.appendChild(botaoRelatorios);
        
        console.log('✅ Botão de relatórios adicionado na barra de navegação');
        return true;
    }
    
    console.log('⚠️ Não foi possível encontrar local para adicionar botão de relatórios');
    return false;
}

// Inicializar quando a página carregar
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(adicionarBotaoRelatorios, 1000);
});