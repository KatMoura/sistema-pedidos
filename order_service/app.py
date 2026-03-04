from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import os
import time
import requests

from models import EmailObserver, LogObserver, TelaObserver
from db import init_db, DB_PATH
from factories import ProdutoFactory, PedidoFactory, get_db_connection

app = Flask(__name__)
CORS(app)
init_db()

# endereços configuráveis
USER_SERVICE = os.environ.get('USER_SERVICE', 'http://localhost:5001')

# --- produtos CRUD ------------------------------------------------

@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, preco FROM produtos')
    produtos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(produtos)

@app.route('/api/produtos', methods=['POST'])
def criar_produto():
    data = request.json
    nome = data.get('nome')
    preco = data.get('preco')
    if not nome or preco is None:
        return jsonify({'error': 'nome e preco obrigatórios'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO produtos (nome, preco) VALUES (?,?)', (nome, preco))
    conn.commit()
    produto_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': produto_id, 'nome': nome, 'preco': preco}), 201

@app.route('/api/produtos/<int:produto_id>', methods=['PUT'])
def atualizar_produto(produto_id):
    data = request.json
    nome = data.get('nome')
    preco = data.get('preco')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE produtos SET nome=?, preco=? WHERE id=?', (nome, preco, produto_id))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'produto não encontrado'}), 404
    conn.commit()
    conn.close()
    return jsonify({'id': produto_id, 'nome': nome, 'preco': preco})

@app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def apagar_produto(produto_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM produtos WHERE id=?', (produto_id,))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'produto não encontrado'}), 404
    conn.commit()
    conn.close()
    return jsonify({'message': 'produto removido'})

# --- pedidos -------------------------------------------------------

@app.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, cliente, status, data_criacao FROM pedidos')
    pedidos = []
    for row in cursor.fetchall():
        pedidos.append({
            'id': row['id'],
            'cliente': row['cliente'],
            'status': row['status'],
            'data_criacao': row['data_criacao']
        })
    conn.close()
    return jsonify(pedidos)


@app.route('/api/pedidos', methods=['POST'])
def criar_pedido():
    data = request.json
    cliente = data.get('cliente')
    produto_ids = data.get('produtos', [])
    # valida cliente via API de usuários
    if not cliente:
        return jsonify({'error': 'cliente é obrigatório'}), 400
    try:
        r = requests.get(f"{USER_SERVICE}/api/usuarios/{cliente}")
        if r.status_code != 200:
            return jsonify({'error': 'cliente não encontrado em usuário-service'}), 404
    except requests.exceptions.RequestException:
        return jsonify({'error': 'falha ao comunicar usuário-service'}), 500

    # buscar objetos Produto via factory
    produtos = []
    for pid in produto_ids:
        p = ProdutoFactory.from_db(pid)
        if p:
            produtos.append(p)
    pedido = PedidoFactory.create(cliente, produtos)
    # registramos observadores exemplares
    pedido.adicionar_observador(EmailObserver())
    pedido.adicionar_observador(LogObserver())
    pedido.adicionar_observador(TelaObserver())

    # persistir em banco
    conn = get_db_connection()
    cursor = conn.cursor()
    now = time.strftime('%d/%m/%Y %H:%M:%S')
    cursor.execute('INSERT INTO pedidos (cliente, status, data_criacao) VALUES (?,?,?)',
                   (pedido.cliente, pedido.status, now))
    pedido_id = cursor.lastrowid
    for prod in produtos:
        cursor.execute('INSERT INTO pedido_produtos (pedido_id, produto_id) VALUES (?,?)',
                       (pedido_id, prod.id))
    cursor.execute('INSERT INTO historico (pedido_id, status, data, observacoes) VALUES (?,?,?,?)',
                   (pedido_id, pedido.status, now, 'Pedido criado'))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Pedido criado', 'pedido_id': pedido_id, 'total': pedido.calcular_total()}), 201

@app.route('/api/pedidos/<int:pedido_id>/status', methods=['PUT'])
def atualizar_status(pedido_id):
    data = request.json
    novo_status = data.get('status')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM pedidos WHERE id=?', (pedido_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({'error': 'pedido não encontrado'}), 404
    status_anterior = row['status']
    cursor.execute('UPDATE pedidos SET status=? WHERE id=?', (novo_status, pedido_id))
    now = time.strftime('%d/%m/%Y %H:%M:%S')
    cursor.execute('INSERT INTO historico (pedido_id, status, data, observacoes) VALUES (?,?,?,?)',
                   (pedido_id, novo_status, now,
                    f'Status alterado de {status_anterior} para {novo_status}'))
    conn.commit()
    conn.close()
    # notificar observadores não persistidos (para demo, recarregamos o pedido)
    pedido = PedidoFactory.from_db(pedido_id)
    if pedido:
        pedido.adicionar_observador(EmailObserver())
        pedido.adicionar_observador(LogObserver())
        pedido.adicionar_observador(TelaObserver())
        pedido.status = novo_status
    return jsonify({'message': 'status atualizado'})

@app.route('/api/pedidos/<int:pedido_id>', methods=['GET'])
def get_pedido(pedido_id):
    pedido = PedidoFactory.from_db(pedido_id)
    if not pedido:
        return jsonify({'error': 'pedido não encontrado'}), 404
    # montar detalhes
    produtos = [{'id': p.id, 'nome': p.nome, 'preco': p.preco} for p in pedido.produtos]
    return jsonify({'id': pedido.id, 'cliente': pedido.cliente, 'status': pedido.status,
                    'total': pedido.calcular_total(), 'produtos': produtos})

if __name__ == '__main__':
    print('Order service rodando na porta 5000')
    app.run(port=5000, debug=True)
