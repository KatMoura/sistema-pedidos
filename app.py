from flask import Flask, render_template, jsonify, request #a base da web 
from flask_cors import CORS #permite que o js do navegador fale com o pyhon
import threading
import time
import json
import sys #gerencia paths dos arquivos
import os #gerencia paths dos arquivos

# Adiciona o diretório atual ao path para importar observer.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from observer import Pedido, Produto, EmailObserver, LogObserver, TelaObserver

app = Flask(__name__)
CORS(app)

# Dados em memória para simulação
pedidos_ativos = {}
historico_pedidos = []  # Lista para histórico completo
pedidos_finalizados = {}  # Dicionário para pedidos entregues ou cancelados
observadores_ativos = {
    'email': EmailObserver(),
    'log': LogObserver(),
    'tela': TelaObserver()
}

@app.route('/')
def index():
    #pagina principal do sistema 
    return render_template('index.html')

@app.route('/api/produtos', methods=['GET']) #um decorador que define a rota e o método HTTP para acessar os produtos disponíveis
def get_produtos():
    #retorna os produtos disponiveis para o cliente escolher
    produtos = [
        {"id": 1, "nome": "Notebook Dell Inspiron", "preco": 3599.90},
        {"id": 2, "nome": "Mouse Wireless Logitech", "preco": 129.90},
        {"id": 3, "nome": "Teclado Mecânico Redragon", "preco": 289.90},
        {"id": 4, "nome": "Monitor LED 24\" Samsung", "preco": 899.90},
        {"id": 5, "nome": "Headset Gamer HyperX", "preco": 349.90},
        {"id": 6, "nome": "Webcam Logitech C920", "preco": 429.90},
        {"id": 7, "nome": "SSD 1TB Kingston", "preco": 399.90},
        {"id": 8, "nome": "Memória RAM 16GB", "preco": 289.90}
    ]
    return jsonify(produtos)

@app.route('/api/pedidos', methods=['GET'])
def get_pedidos():
    # Retorna a lista de pedidos ativos
    pedidos_list = []
    for pedido_id, pedido_data in pedidos_ativos.items():
        pedidos_list.append({
            'id': pedido_id,
            'cliente': pedido_data['pedido'].cliente,
            'status': pedido_data['pedido'].status,
            'total': pedido_data['pedido'].calcular_total(),
            'quantidade_produtos': len(pedido_data['pedido'].produtos),
            'data_criacao': pedido_data['data_criacao']
        })
    return jsonify(pedidos_list)

@app.route('/api/pedidos/historico', methods=['GET'])
def get_historico_pedidos():
    # Retorna o histórico de pedidos finalizados
    historico_list = []
    for pedido_id, pedido_data in pedidos_finalizados.items():
        historico_list.append({
            'id': pedido_id,
            'cliente': pedido_data['pedido'].cliente,
            'status': pedido_data['pedido'].status,
            'total': pedido_data['pedido'].calcular_total(),
            'quantidade_produtos': len(pedido_data['pedido'].produtos),
            'data_criacao': pedido_data['data_criacao'],
            'data_finalizacao': pedido_data['data_finalizacao'],
            'dias_ativos': pedido_data.get('dias_ativos', 0)
        })
    
    # Ordenar por data de finalização (mais recente primeiro)
    historico_list.sort(key=lambda x: x['data_finalizacao'], reverse=True)
    return jsonify(historico_list)

@app.route('/api/pedidos', methods=['POST']) #mesma coisa do GET, mas para criar um novo pedido
def criar_pedido():
    #cria um novo pedido com os dados enviados pelo cliente (nome e produtos selecionados)
    data = request.json
    cliente = data.get('cliente')
    produtos_ids = data.get('produtos', [])
    
    if not cliente:
        return jsonify({'error': 'Nome do cliente é obrigatório'}), 400
    
    # Cria o pedido
    pedido = Pedido(cliente)
    
    # Adiciona produtos
    produtos_disponiveis = {
        1: Produto("Notebook Dell Inspiron", 3599.90),
        2: Produto("Mouse Wireless Logitech", 129.90),
        3: Produto("Teclado Mecânico Redragon", 289.90),
        4: Produto("Monitor LED 24\" Samsung", 899.90),
        5: Produto("Headset Gamer HyperX", 349.90),
        6: Produto("Webcam Logitech C920", 429.90),
        7: Produto("SSD 1TB Kingston", 399.90),
        8: Produto("Memória RAM 16GB", 289.90)
    }
    
    for produto_id in produtos_ids:
        if produto_id in produtos_disponiveis:
            pedido.adicionar_produto(produtos_disponiveis[produto_id])
    
    # Registra observadores ativos
    observadores_selecionados = data.get('observadores', ['email', 'log', 'tela'])
    for obs in observadores_selecionados:
        if obs in observadores_ativos:
            pedido.adicionar_observador(observadores_ativos[obs])

    # Armazena o pedido
    pedido_id = pedido.id
    data_criacao = time.strftime('%d/%m/%Y %H:%M:%S')
    pedidos_ativos[pedido_id] = {
        'pedido': pedido,
        'historico': [{
            'status': pedido.status,
            'data': data_criacao,
            'observacoes': 'Pedido criado'
        }],
        'data_criacao': data_criacao
    }
    
    return jsonify({
        'message': 'Pedido criado com sucesso',
        'pedido_id': pedido_id,
        'status': pedido.status,
        'total': pedido.calcular_total()
    })

@app.route('/api/pedidos/<int:pedido_id>/status', methods=['PUT']) #mesma coisa das outras, mas para atualizar o status de um pedido específico
def atualizar_status(pedido_id):
    #atualiza o status de um pedido específico e registra a mudança no histórico
    data = request.json
    novo_status = data.get('status')
    
    if pedido_id not in pedidos_ativos:
        return jsonify({'error': 'Pedido não encontrado'}), 404
    
    pedido = pedidos_ativos[pedido_id]['pedido']
    status_anterior = pedido.status
    
    # Atualiza o status (isso disparará as notificações dos observadores)
    pedido.status = novo_status
    
    # Registra no histórico
    data_alteracao = time.strftime('%d/%m/%Y %H:%M:%S')
    pedidos_ativos[pedido_id]['historico'].append({
        'status': novo_status,
        'data': data_alteracao,
        'observacoes': f'Status alterado de {status_anterior} para {novo_status}'
    })
    
    # Se o pedido foi entregue ou cancelado, mover para histórico
    if novo_status in [Pedido.STATUS_ENTREGUE, Pedido.STATUS_CANCELADO]:
        # Calcular dias ativos (simulação)
        data_criacao = pedidos_ativos[pedido_id]['data_criacao']
        dias_ativos = 1  # Em um sistema real, calcularíamos a diferença de dias
        
        # Mover para histórico
        pedidos_finalizados[pedido_id] = {
            'pedido': pedido,
            'historico': pedidos_ativos[pedido_id]['historico'],
            'data_criacao': data_criacao,
            'data_finalizacao': data_alteracao,
            'dias_ativos': dias_ativos
        }
        
        # Remover dos pedidos ativos
        del pedidos_ativos[pedido_id]
        
        return jsonify({
            'message': f'Status atualizado para {novo_status}. Pedido movido para histórico.',
            'pedido_id': pedido_id,
            'status_anterior': status_anterior,
            'status_novo': novo_status,
            'movido_para_historico': True
        })
    
    return jsonify({
        'message': 'Status atualizado com sucesso',
        'pedido_id': pedido_id,
        'status_anterior': status_anterior,
        'status_novo': novo_status,
        'movido_para_historico': False
    })

@app.route('/api/pedidos/<int:pedido_id>', methods=['GET'])
def get_pedido_detalhes(pedido_id):
    #retorna os detalhes de um pedido específico, seja ativo ou finalizado
    # Verificar primeiro nos pedidos ativos
    if pedido_id in pedidos_ativos:
        pedido_data = pedidos_ativos[pedido_id]
        pedido = pedido_data['pedido']
        tipo = 'ativo'
    elif pedido_id in pedidos_finalizados:
        pedido_data = pedidos_finalizados[pedido_id]
        pedido = pedido_data['pedido']
        tipo = 'finalizado'
    else:
        return jsonify({'error': 'Pedido não encontrado'}), 404
    
    detalhes = {
        'id': pedido.id,
        'cliente': pedido.cliente,
        'status': pedido.status,
        'total': pedido.calcular_total(),
        'produtos': [{'nome': p.nome, 'preco': p.preco} for p in pedido.produtos],
        'historico': pedido_data['historico'],
        'tipo': tipo,
        'data_criacao': pedido_data.get('data_criacao', 'N/A'),
        'data_finalizacao': pedido_data.get('data_finalizacao', 'N/A') if tipo == 'finalizado' else None
    }
    
    return jsonify(detalhes)

@app.route('/api/estatisticas', methods=['GET'])
def get_estatisticas():
    #retorna estatísticas básicas sobre os pedidos
    total_pedidos = len(pedidos_ativos) + len(pedidos_finalizados)
    pedidos_entregues = sum(1 for p in pedidos_finalizados.values() 
                          if p['pedido'].status == Pedido.STATUS_ENTREGUE)
    pedidos_cancelados = sum(1 for p in pedidos_finalizados.values() 
                           if p['pedido'].status == Pedido.STATUS_CANCELADO)
    
    # Calcular valor total vendido (apenas pedidos entregues)
    valor_total_vendido = sum(p['pedido'].calcular_total() 
                            for p in pedidos_finalizados.values() 
                            if p['pedido'].status == Pedido.STATUS_ENTREGUE)
    
    return jsonify({
        'pedidos_ativos': len(pedidos_ativos),
        'pedidos_finalizados': len(pedidos_finalizados),
        'pedidos_entregues': pedidos_entregues,
        'pedidos_cancelados': pedidos_cancelados,
        'total_pedidos': total_pedidos,
        'valor_total_vendido': valor_total_vendido,
        'taxa_entrega': (pedidos_entregues / max(total_pedidos, 1)) * 100
    })

@app.route('/api/notificacoes', methods=['GET'])
def get_notificacoes():
    #retorna notificações simuladas para o sistema
    return jsonify({
        'notificacoes': [
            'Sistema iniciado. Aguardando pedidos...'
        ]
    })

@app.route('/api/observadores', methods=['GET'])
def get_observadores():
    # Retorna a lista de observadores disponíveis
    return jsonify([
        {'id': 'email', 'nome': 'Notificação por E-mail', 'descricao': 'Envia e-mails para o cliente'},
        {'id': 'log', 'nome': 'Registro em Log', 'descricao': 'Registra todas as alterações em arquivo de log'},
        {'id': 'tela', 'nome': 'Notificação na Tela', 'descricao': 'Exibe notificações na interface'}
    ])

if __name__ == '__main__':
    
    print("SISTEMA DE GERENCIAMENTO DE PEDIDOS - INTERFACE WEB")
    print("Servidor iniciado em: http://localhost:5000")
    print("Acesse o navegador e abra o endereço acima")
   
    
    app.run(debug=True, port=5000)