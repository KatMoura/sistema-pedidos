document.addEventListener('DOMContentLoaded', function() {
    // API base URLs (microservices)
    const API_ORDERS = 'http://localhost:5000';
    const API_USERS  = 'http://localhost:5001';

    // Elementos do DOM
    const productList = document.getElementById('product-list');
    const selectedProductsList = document.getElementById('selected-products-list');
    const selectedTotal = document.getElementById('selected-total');
    const customerNameInput = document.getElementById('customer-name');
    const createOrderBtn = document.getElementById('create-order-btn');
    const ordersList = document.getElementById('orders-list');
    const historicoList = document.getElementById('historico-list');
    const notifications = document.getElementById('notifications');
    const orderDetails = document.getElementById('order-details');
    const statsBar = document.getElementById('stats-bar');
    
    // Elementos das tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Filtros do histórico
    const filterStatus = document.getElementById('filter-status');
    const filterCliente = document.getElementById('filter-cliente');
    const clearFiltersBtn = document.getElementById('clear-filters');
    
    // Estatísticas
    const estatisticas = {
        totalPedidos: document.getElementById('stat-total-pedidos'),
        entregues: document.getElementById('stat-entregues'),
        cancelados: document.getElementById('stat-cancelados'),
        valorTotal: document.getElementById('stat-valor-total'),
        progressFill: document.getElementById('progress-fill'),
        progressText: document.getElementById('progress-text')
    };
    
    // Modal elements
    const statusModal = document.getElementById('status-modal');
    const closeModalBtn = document.querySelector('.close-modal');
    const cancelStatusBtn = document.getElementById('cancel-status-btn');
    const statusButtons = document.querySelectorAll('.status-btn');
    const modalWarning = document.getElementById('modal-warning');
    
    // Estado da aplicação
    let selectedProducts = [];
    let currentOrderIdForModal = null;
    
    // Inicializar tabs
    function initTabs() {
        tabBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const tabId = this.dataset.tab;
                
                // Remover classe active de todas as tabs
                tabBtns.forEach(b => b.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));
                
                // Adicionar classe active à tab clicada
                this.classList.add('active');
                document.getElementById(`tab-${tabId}`).classList.add('active');
                
                // Carregar conteúdo da tab
                if (tabId === 'ativos') {
                    loadOrders();
                } else if (tabId === 'historico') {
                    loadHistorico();
                    loadEstatisticas();
                } else if (tabId === 'criar') {
                    loadProducts();
                }
            });
        });
    }
    
   
    // Carregar produtos disponíveis
    function loadProducts() {
        fetch(`${API_ORDERS}/api/produtos`)
            .then(response => response.json())
            .then(products => {
                displayProducts(products);
            })
            .catch(error => {
                console.error('Erro ao carregar produtos:', error);
                showNotification('error', 'Erro ao carregar produtos', 'Tente recarregar a página');
            });
    }
    
    // Exibir produtos na lista
    function displayProducts(products) {
        productList.innerHTML = '';
        
        products.forEach(product => {
            const productElement = document.createElement('div');
            productElement.className = 'product-item';
            productElement.dataset.id = product.id;
            
            productElement.innerHTML = `
                <div class="product-info">
                    <h4>${product.nome}</h4>
                    <div class="product-price">R$ ${product.preco.toFixed(2)}</div>
                </div>
                <div class="product-actions">
                    <button class="add-product-btn" data-id="${product.id}">
                        <i class="fas fa-plus"></i> Adicionar
                    </button>
                </div>
            `;
            
            productList.appendChild(productElement);
        });
        
        // Adicionar event listeners aos botões
        document.querySelectorAll('.add-product-btn').forEach(button => {
            button.addEventListener('click', function() {
                const productId = parseInt(this.dataset.id);
                addProductToSelection(productId);
            });
        });
    }
    
    // Adicionar produto à seleção
    function addProductToSelection(productId) {
        fetch(`${API_ORDERS}/api/produtos`)
            .then(response => response.json())
            .then(products => {
                const product = products.find(p => p.id === productId);
                
                if (product) {
                    // Verificar se o produto já está selecionado
                    const existingIndex = selectedProducts.findIndex(p => p.id === productId);
                    
                    if (existingIndex === -1) {
                        selectedProducts.push({
                            id: product.id,
                            nome: product.nome,
                            preco: product.preco,
                            quantidade: 1
                        });
                    } else {
                        selectedProducts[existingIndex].quantidade++;
                    }
                    
                    updateSelectedProductsList();
                }
            });
    }
    
    // Remover produto da seleção
    function removeProductFromSelection(productId) {
        const existingIndex = selectedProducts.findIndex(p => p.id === productId);
        
        if (existingIndex !== -1) {
            if (selectedProducts[existingIndex].quantidade > 1) {
                selectedProducts[existingIndex].quantidade--;
            } else {
                selectedProducts.splice(existingIndex, 1);
            }
            
            updateSelectedProductsList();
        }
    }
    
    // Atualizar lista de produtos selecionados
    function updateSelectedProductsList() {
        if (selectedProducts.length === 0) {
            selectedProductsList.innerHTML = '<div class="empty-selection">Nenhum produto selecionado</div>';
            selectedTotal.textContent = '0.00';
            return;
        }
        
        let html = '';
        let total = 0;
        
        selectedProducts.forEach(product => {
            const subtotal = product.preco * product.quantidade;
            total += subtotal;
            
            html += `
                <div class="selected-product-item">
                    <div class="product-info">
                        <div class="product-name">${product.nome}</div>
                        <div class="product-quantity">Quantidade: ${product.quantidade}</div>
                    </div>
                    <div class="product-actions">
                        <button class="remove-product-btn" data-id="${product.id}">
                            <i class="fas fa-minus"></i>
                        </button>
                        <div class="product-subtotal">R$ ${subtotal.toFixed(2)}</div>
                    </div>
                </div>
            `;
        });
        
        selectedProductsList.innerHTML = html;
        selectedTotal.textContent = total.toFixed(2);
        
        // Adicionar event listeners aos botões de remover
        document.querySelectorAll('.remove-product-btn').forEach(button => {
            button.addEventListener('click', function() {
                const productId = parseInt(this.dataset.id);
                removeProductFromSelection(productId);
            });
        });
    }
    

    // Carregar pedidos ativos
    function loadOrders() {
        fetch(`${API_ORDERS}/api/pedidos`)
            .then(response => response.json())
            .then(orders => {
                displayOrders(orders);
            })
            .catch(error => {
                console.error('Erro ao carregar pedidos:', error);
            });
    }
    
    // Exibir pedidos na lista
    function displayOrders(orders) {
        if (orders.length === 0) {
            ordersList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-clipboard"></i>
                    <p>Nenhum pedido ativo no momento</p>
                    <p>Crie um novo pedido para começar</p>
                </div>
            `;
            return;
        }
        
        ordersList.innerHTML = '';
        
        orders.forEach(order => {
            const orderElement = document.createElement('div');
            orderElement.className = 'order-item';
            orderElement.dataset.id = order.id;
            
            // Determinar classe de status
            const statusClass = `status-${order.status.toLowerCase()}`;
            
            orderElement.innerHTML = `
                <div class="order-info">
                    <h4>Pedido #${order.id} - ${order.cliente}</h4>
                    <div>Total: R$ ${order.total.toFixed(2)}</div>
                    <div>Produtos: ${order.quantidade_produtos}</div>
                    <div class="order-status ${statusClass}">${order.status}</div>
                </div>
                <div class="order-actions">
                    <button class="view-order-btn" data-id="${order.id}">
                        <i class="fas fa-eye"></i> Detalhes
                    </button>
                    <button class="update-status-btn" data-id="${order.id}">
                        <i class="fas fa-edit"></i> Alterar Status
                    </button>
                </div>
            `;
            
            ordersList.appendChild(orderElement);
        });
        
        // Adicionar event listeners aos botões
        document.querySelectorAll('.view-order-btn').forEach(button => {
            button.addEventListener('click', function() {
                const orderId = parseInt(this.dataset.id);
                viewOrderDetails(orderId);
            });
        });
        
        document.querySelectorAll('.update-status-btn').forEach(button => {
            button.addEventListener('click', function() {
                const orderId = parseInt(this.dataset.id);
                openStatusModal(orderId);
            });
        });
    }
    
    // Ver detalhes do pedido
    function viewOrderDetails(orderId) {
        fetch(`${API_ORDERS}/api/pedidos/${orderId}`)
            .then(response => response.json())
            .then(order => {
                if (order.error) {
                    showNotification('error', 'Erro', order.error);
                    return;
                }
                
                displayOrderDetails(order);
            })
            .catch(error => {
                console.error('Erro ao carregar detalhes do pedido:', error);
                showNotification('error', 'Erro', 'Não foi possível carregar os detalhes do pedido');
            });
    }
    
    // Exibir detalhes do pedido
    function displayOrderDetails(order) {
        // Determinar classe de status
        const statusClass = `status-${order.status.toLowerCase()}`;
        
        let productsHtml = '';
        order.produtos.forEach(product => {
            productsHtml += `
                <li>
                    <span>${product.nome}</span>
                    <span>R$ ${product.preco.toFixed(2)}</span>
                </li>
            `;
        });
        
        let historyHtml = '';
        order.historico.forEach(item => {
            historyHtml += `
                <div class="history-item">
                    <div class="history-status">${item.status}</div>
                    <div class="history-time">${item.data}</div>
                    <div class="history-notes">${item.observacoes}</div>
                </div>
            `;
        });
        
        const tipoText = order.tipo === 'ativo' ? ' (Ativo)' : ' (Finalizado)';
        
        orderDetails.innerHTML = `
            <div class="detail-item">
                <strong>ID do Pedido</strong>
                <div>#${order.id}${tipoText}</div>
            </div>
            <div class="detail-item">
                <strong>Cliente</strong>
                <div>${order.cliente}</div>
            </div>
            <div class="detail-item">
                <strong>Status</strong>
                <div class="order-status ${statusClass}">${order.status}</div>
            </div>
            <div class="detail-item">
                <strong>Produtos</strong>
                <ul class="detail-products">
                    ${productsHtml}
                </ul>
            </div>
            <div class="detail-item">
                <strong>Total</strong>
                <div>R$ ${order.total.toFixed(2)}</div>
            </div>
            <div class="detail-item">
                <strong>Data de Criação</strong>
                <div>${order.data_criacao}</div>
            </div>
            ${order.data_finalizacao ? `
                <div class="detail-item">
                    <strong>Data de Finalização</strong>
                    <div>${order.data_finalizacao}</div>
                </div>
            ` : ''}
            <div class="detail-item">
                <strong>Histórico de Alterações</strong>
                <div class="order-history">
                    ${historyHtml}
                </div>
            </div>
        `;
    }
    
 
    
    // Carregar estatísticas
    function loadEstatisticas() {
        fetch(`${API_ORDERS}/api/estatisticas`)
            .then(response => response.json())
            .then(data => {
                estatisticas.totalPedidos.textContent = data.total_pedidos;
                estatisticas.entregues.textContent = data.pedidos_entregues;
                estatisticas.cancelados.textContent = data.pedidos_cancelados;
                estatisticas.valorTotal.textContent = `R$ ${data.valor_total_vendido.toFixed(2)}`;
                
                // Atualizar barra de progresso
                const taxa = Math.round(data.taxa_entrega);
                estatisticas.progressFill.style.width = `${taxa}%`;
                estatisticas.progressText.textContent = `${taxa}%`;
                
                // Atualizar badges das tabs
                document.getElementById('tab-badge-ativos').textContent = data.pedidos_ativos;
                document.getElementById('tab-badge-historico').textContent = data.pedidos_finalizados;
                
                // Atualizar stats bar no header
                updateStatsBar(data);
            })
            .catch(error => {
                console.error('Erro ao carregar estatísticas:', error);
            });
    }
    
    // Atualizar stats bar no header
    function updateStatsBar(data) {
        statsBar.innerHTML = `
            <div class="stat-item">
                <i class="fas fa-spinner"></i>
                <span>Ativos: ${data.pedidos_ativos}</span>
            </div>
            <div class="stat-item">
                <i class="fas fa-history"></i>
                <span>Histórico: ${data.pedidos_finalizados}</span>
            </div>
            <div class="stat-item">
                <i class="fas fa-check-circle"></i>
                <span>Entregues: ${data.pedidos_entregues}</span>
            </div>
            <div class="stat-item">
                <i class="fas fa-money-bill-wave"></i>
                <span>Total: R$ ${data.valor_total_vendido.toFixed(2)}</span>
            </div>
        `;
    }
    
    // Carregar histórico de pedidos
    function loadHistorico() {
        fetch(`${API_ORDERS}/api/pedidos/historico`)
            .then(response => response.json())
            .then(pedidos => {
                displayHistorico(pedidos);
                
                // Atualizar filtro de clientes
                updateClienteFilter(pedidos);
            })
            .catch(error => {
                console.error('Erro ao carregar histórico:', error);
            });
    }
    
    // Exibir histórico de pedidos
    function displayHistorico(pedidos) {
        if (pedidos.length === 0) {
            historicoList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-history"></i>
                    <p>Nenhum pedido no histórico</p>
                    <p>Os pedidos aparecerão aqui após serem entregues ou cancelados</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        
        // Aplicar filtros
        let pedidosFiltrados = pedidos;
        
        if (filterStatus.value) {
            pedidosFiltrados = pedidosFiltrados.filter(p => p.status === filterStatus.value);
        }
        
        if (filterCliente.value) {
            pedidosFiltrados = pedidosFiltrados.filter(p => p.cliente === filterCliente.value);
        }
        
        if (pedidosFiltrados.length === 0) {
            historicoList.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-search"></i>
                    <p>Nenhum pedido encontrado com os filtros atuais</p>
                </div>
            `;
            return;
        }
        
        pedidosFiltrados.forEach(pedido => {
            const statusClass = `status-${pedido.status.toLowerCase()}`;
            
            html += `
                <div class="historico-item" data-id="${pedido.id}">
                    <div class="historico-header">
                        <div class="historico-info">
                            <h4>Pedido #${pedido.id} - ${pedido.cliente}</h4>
                            <div class="order-status ${statusClass}">${pedido.status}</div>
                        </div>
                        <div class="historico-total">
                            <strong>R$ ${pedido.total.toFixed(2)}</strong>
                        </div>
                    </div>
                    <div class="historico-details">
                        <div>Produtos: ${pedido.quantidade_produtos}</div>
                        <div class="historico-dates">
                            <span><i class="far fa-calendar-plus"></i> Criado: ${pedido.data_criacao}</span>
                            <span><i class="far fa-calendar-check"></i> Finalizado: ${pedido.data_finalizacao}</span>
                            <span><i class="far fa-clock"></i> Dias ativos: ${pedido.dias_ativos}</span>
                        </div>
                    </div>
                </div>
            `;
        });
        
        historicoList.innerHTML = html;
        
        // Adicionar event listeners aos itens do histórico
        document.querySelectorAll('.historico-item').forEach(item => {
            item.addEventListener('click', function() {
                const orderId = parseInt(this.dataset.id);
                viewOrderDetails(orderId);
            });
        });
    }
    
    // Atualizar filtro de clientes
    function updateClienteFilter(pedidos) {
        const clientes = [...new Set(pedidos.map(p => p.cliente))];
        const filterSelect = document.getElementById('filter-cliente');
        
        // Salvar valor atual
        const currentValue = filterSelect.value;
        
        // Limpar opções exceto a primeira
        while (filterSelect.options.length > 1) {
            filterSelect.remove(1);
        }
        
        // Adicionar clientes únicos
        clientes.sort().forEach(cliente => {
            const option = document.createElement('option');
            option.value = cliente;
            option.textContent = cliente;
            filterSelect.appendChild(option);
        });
        
        // Restaurar valor anterior se ainda existir
        if (currentValue && clientes.includes(currentValue)) {
            filterSelect.value = currentValue;
        }
    }
    
    // Aplicar filtros
    function applyFilters() {
        loadHistorico();
    }
    
 
    
    // Abrir modal para alterar status (atualizada para mostrar warning)
    function openStatusModal(orderId) {
        currentOrderIdForModal = orderId;
        
        // Obter informações do pedido
        fetch(`${API_ORDERS}/api/pedidos/${orderId}`)
            .then(response => response.json())
            .then(order => {
                if (order.error) {
                    showNotification('error', 'Erro', order.error);
                    return;
                }
                
                document.getElementById('modal-order-id').textContent = order.id;
                document.getElementById('modal-customer-name').textContent = order.cliente;
                
                // Mostrar warning se o pedido estiver ativo e for mudar para entregue/cancelado
                const isActive = order.tipo === 'ativo';
                modalWarning.style.display = isActive ? 'flex' : 'none';
                
                statusModal.style.display = 'flex';
            })
            .catch(error => {
                console.error('Erro ao carregar pedido:', error);
            });
    }
    
    // Fechar modal
    function closeStatusModal() {
        statusModal.style.display = 'none';
        currentOrderIdForModal = null;
        modalWarning.style.display = 'none';
    }
    
    // Atualizar status do pedido (atualizada para lidar com movimentação para histórico)
    function updateOrderStatus(newStatus) {
        if (!currentOrderIdForModal) return;
        
        fetch(`${API_ORDERS}/api/pedidos/${currentOrderIdForModal}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showNotification('error', 'Erro', data.error);
                return;
            }
            
            if (data.movido_para_historico) {
                showNotification('success', 'Pedido Finalizado', 
                    `Pedido #${data.pedido_id} foi ${newStatus.toLowerCase()} e movido para o histórico`);
                
                // Atualizar ambas as tabs
                loadOrders();
                loadHistorico();
                loadEstatisticas();
            } else {
                showNotification('success', 'Status Atualizado', 
                    `Status do pedido #${data.pedido_id} alterado para "${data.status_novo}"`);
                
                // Atualizar apenas pedidos ativos
                loadOrders();
            }
            
            // Fechar modal
            closeStatusModal();
            
            // Atualizar detalhes se estiverem visíveis
            if (orderDetails.innerHTML.includes(`#${data.pedido_id}`)) {
                viewOrderDetails(data.pedido_id);
            }
        })
        .catch(error => {
            console.error('Erro ao atualizar status:', error);
            showNotification('error', 'Erro', 'Não foi possível atualizar o status');
        });
    }
    
  
    
    // Criar um novo pedido (atualizada para voltar à tab de ativos)
    function createOrder() {
        const customerName = customerNameInput.value.trim();
        
        if (!customerName) {
            showNotification('error', 'Erro', 'Digite o nome do cliente');
            customerNameInput.focus();
            return;
        }
        
        if (selectedProducts.length === 0) {
            showNotification('error', 'Erro', 'Selecione pelo menos um produto');
            return;
        }
        
        // Obter observadores selecionados
        const observadores = [];
        if (document.getElementById('observer-email').checked) observadores.push('email');
        if (document.getElementById('observer-log').checked) observadores.push('log');
        if (document.getElementById('observer-tela').checked) observadores.push('tela');
        
        const orderData = {
            cliente: customerName,
            produtos: selectedProducts.map(p => p.id),
            observadores: observadores
        };
        
        fetch(`${API_ORDERS}/api/pedidos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showNotification('error', 'Erro', data.error);
                return;
            }
            
            showNotification('success', 'Pedido Criado', 
                `Pedido #${data.pedido_id} criado com sucesso para ${customerName}`);
            
            // Limpar formulário
            customerNameInput.value = '';
            selectedProducts = [];
            updateSelectedProductsList();
            
            // Mudar para tab de pedidos ativos
            document.querySelector('[data-tab="ativos"]').click();
            
            // Atualizar lista de pedidos e estatísticas
            loadOrders();
            loadEstatisticas();
        })
        .catch(error => {
            console.error('Erro ao criar pedido:', error);
            showNotification('error', 'Erro', 'Não foi possível criar o pedido');
        });
    }
    

    // Mostrar notificação
    function showNotification(type, title, message) {
        const notificationItem = document.createElement('div');
        notificationItem.className = 'notification-item';
        
        let icon = 'fa-info-circle';
        if (type === 'success') icon = 'fa-check-circle';
        if (type === 'error') icon = 'fa-exclamation-circle';
        if (type === 'warning') icon = 'fa-exclamation-triangle';
        
        const now = new Date();
        const timeString = now.toLocaleTimeString('pt-BR', { 
            hour: '2-digit', 
            minute: '2-digit',
            second: '2-digit'
        });
        
        notificationItem.innerHTML = `
            <div class="notification-icon">
                <i class="fas ${icon}"></i>
            </div>
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-time">${timeString}</div>
                <div class="notification-message">${message}</div>
            </div>
        `;
        
        // Adicionar no início da lista
        notifications.insertBefore(notificationItem, notifications.firstChild);
        
        // Limitar número de notificações
        const notificationItems = notifications.querySelectorAll('.notification-item');
        if (notificationItems.length > 10) {
            notifications.removeChild(notificationItems[notificationItems.length - 1]);
        }
        
        // Remover automaticamente após 10 segundos
        setTimeout(() => {
            if (notificationItem.parentNode) {
                notificationItem.style.opacity = '0';
                notificationItem.style.transition = 'opacity 0.5s ease';
                
                setTimeout(() => {
                    if (notificationItem.parentNode) {
                        notifications.removeChild(notificationItem);
                    }
                }, 500);
            }
        }, 10000);
    }
    

    
    // Inicializar
    function init() {
        initTabs();
        loadProducts();
        loadOrders();
        loadEstatisticas();
        
        // Event listeners
        createOrderBtn.addEventListener('click', createOrder);
        
        customerNameInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                createOrder();
            }
        });
        
        // Filtros do histórico
        filterStatus.addEventListener('change', applyFilters);
        filterCliente.addEventListener('change', applyFilters);
        clearFiltersBtn.addEventListener('click', function() {
            filterStatus.value = '';
            filterCliente.value = '';
            applyFilters();
        });
        
        // Modal event listeners
        closeModalBtn.addEventListener('click', closeStatusModal);
        cancelStatusBtn.addEventListener('click', closeStatusModal);
        
        // Fechar modal ao clicar fora
        window.addEventListener('click', function(e) {
            if (e.target === statusModal) {
                closeStatusModal();
            }
        });
        
        // Event listeners para botões de status
        statusButtons.forEach(button => {
            button.addEventListener('click', function() {
                const newStatus = this.dataset.status;
                updateOrderStatus(newStatus);
            });
        });
        
        // Atualizar dados a cada 10 segundos
        setInterval(() => {
            const activeTab = document.querySelector('.tab-content.active').id;
            
            if (activeTab === 'tab-ativos') {
                loadOrders();
            } else if (activeTab === 'tab-historico') {
                loadHistorico();
                loadEstatisticas();
            }
        }, 10000);
        
        // Mostrar notificação inicial
        showNotification('info', 'Sistema Iniciado', 
            'Sistema de gerenciamento de pedidos está pronto para uso. Crie um novo pedido para começar.');
    }
    
    // Iniciar aplicação
    init();
});