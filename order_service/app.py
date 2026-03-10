from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
import os
import time
import requests
from dotenv import load_dotenv

from models import EmailObserver, LogObserver, TelaObserver
from factories import ProdutoFactory, PedidoFactory

load_dotenv()

app = Flask(__name__)
CORS(app)

# Inicializar Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = (
    os.environ.get('SUPABASE_KEY')
    or os.environ.get('SUPABASE_ANON_KEY')
    or os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
)

if not SUPABASE_URL:
    raise RuntimeError('SUPABASE_URL nao definido no ambiente')
if not SUPABASE_KEY:
    raise RuntimeError(
        'SUPABASE_KEY ausente. Use a anon key ou a service role key do Supabase.'
    )
if SUPABASE_KEY.startswith('sb_publishable_'):
    raise RuntimeError(
        'SUPABASE_KEY invalido. Esse e um publishable key; use a anon key ou a service role key.'
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Endereço do user service
USER_SERVICE = os.environ.get('USER_SERVICE', 'http://localhost:5001')

def init_db():
    """Verifica se as tabelas existem no Supabase"""
    try:
        supabase.table('produtos').select('*').limit(1).execute()
        supabase.table('pedidos').select('*').limit(1).execute()
        supabase.table('pedido_produtos').select('*').limit(1).execute()
        supabase.table('historico').select('*').limit(1).execute()
        print("Todas as tabelas existem")
    except Exception as e:
        print(f"Erro ao verificar tabelas: {e}")

# --- PRODUTOS CRUD ----

def seed_produtos():
    produtos_iniciais = [
        {"nome": "Hambúrguer Clássico", "preco": 22.90},
        {"nome": "X-Bacon", "preco": 27.50},
        {"nome": "Batata Frita", "preco": 14.00},
        {"nome": "Refrigerante Lata", "preco": 6.50},
        {"nome": "Suco Natural", "preco": 8.00},
        {"nome": "Pizza Calabresa", "preco": 49.90},
        {"nome": "Pizza Margherita", "preco": 47.90},
        {"nome": "Água Mineral", "preco": 4.00},
    ]

    for p in produtos_iniciais:
        existe = (
            supabase.table("produtos")
            .select("id")
            .eq("nome", p["nome"])
            .limit(1)
            .execute()
            .data
            or []
        )
        if not existe:
            supabase.table("produtos").insert(p).execute()

@app.route('/api/produtos', methods=['GET'])
def listar_produtos():
    try:
        response = supabase.table('produtos').select('*').execute()
        produtos = response.data if response.data else []
        return jsonify(produtos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produtos', methods=['POST'])
def criar_produto():
    data = request.json
    nome = data.get('nome')
    preco = data.get('preco')
    
    if not nome or preco is None:
        return jsonify({'error': 'nome e preco obrigatórios'}), 400
    
    try:
        response = supabase.table('produtos').insert({
            'nome': nome,
            'preco': preco
        }).execute()
        
        produto = response.data[0] if response.data else None
        return jsonify({
            'id': produto['id'],
            'nome': produto['nome'],
            'preco': produto['preco']
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produtos/<int:produto_id>', methods=['PUT'])
def atualizar_produto(produto_id):
    data = request.json
    nome = data.get('nome')
    preco = data.get('preco')
    
    try:
        response = supabase.table('produtos').update({
            'nome': nome,
            'preco': preco
        }).eq('id', produto_id).execute()
        
        if not response.data:
            return jsonify({'error': 'produto não encontrado'}), 404
        
        produto = response.data[0]
        return jsonify({
            'id': produto['id'],
            'nome': produto['nome'],
            'preco': produto['preco']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/produtos/<int:produto_id>', methods=['DELETE'])
def apagar_produto(produto_id):
    try:
        response = supabase.table('produtos').delete().eq('id', produto_id).execute()
        
        if not response.data:
            return jsonify({'error': 'produto não encontrado'}), 404
        
        return jsonify({'message': 'produto removido'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# --- PEDIDOS ----

@app.route('/api/pedidos', methods=['GET'])
def listar_pedidos():
    try:
        response = supabase.table('pedidos').select('*').execute()
        pedidos = []
        
        for row in response.data:
            # Buscar produtos do pedido
            produtos_response = supabase.table('pedido_produtos').select(
                'produto_id'
            ).eq('pedido_id', row['id']).execute()
            
            quantidade_produtos = len(produtos_response.data) if produtos_response.data else 0
            
            pedidos.append({
                'id': row['id'],
                'cliente': row['cliente'],
                'status': row['status'],
                'data_criacao': row['data_criacao'],
                'quantidade_produtos': quantidade_produtos,
                'total': 0  # Será calculado no frontend ou incluir join
            })
        
        return jsonify(pedidos)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pedidos', methods=['POST'])
def criar_pedido():
    data = request.json
    cliente = data.get('cliente')
    produto_ids = data.get('produtos', [])
    
    if not cliente:
        return jsonify({'error': 'cliente é obrigatório'}), 400
    
    try:
        # Validar cliente via user service
        r = requests.get(f"{USER_SERVICE}/api/usuarios")
        usuarios = r.json()
        cliente_existe = any(u.get('nome') == cliente for u in usuarios)
        
        if not cliente_existe:
            # Se não encontra pelo name, continua mesmo assim (cliente pode ser livremente nomeado)
            pass
        
        # Criar pedido
        now = time.strftime('%d/%m/%Y %H:%M:%S')
        
        response = supabase.table('pedidos').insert({
            'cliente': cliente,
            'status': 'Pendente',
            'data_criacao': now,
            'data_finalizacao': None
        }).execute()
        
        if not response.data:
            return jsonify({'error': 'Falha ao criar pedido'}), 500
        
        pedido_id = response.data[0]['id']
        
        # Adicionar produtos ao pedido
        for produto_id in produto_ids:
            supabase.table('pedido_produtos').insert({
                'pedido_id': pedido_id,
                'produto_id': produto_id
            }).execute()
        
        # Adicionar ao histórico
        supabase.table('historico').insert({
            'pedido_id': pedido_id,
            'status': 'Pendente',
            'data': now,
            'observacoes': 'Pedido criado'
        }).execute()
        
        # Calcular total
        total = 0
        for pid in produto_ids:
            prod_response = supabase.table('produtos').select('preco').eq('id', pid).execute()
            if prod_response.data:
                total += prod_response.data[0]['preco']
        
        return jsonify({
            'message': 'Pedido criado',
            'pedido_id': pedido_id,
            'total': total
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pedidos/<int:pedido_id>/status', methods=['PUT'])
def atualizar_status(pedido_id):
    data = request.json
    novo_status = data.get('status')
    
    try:
        # Buscar status anterior
        response = supabase.table('pedidos').select('status').eq('id', pedido_id).execute()
        
        if not response.data:
            return jsonify({'error': 'pedido não encontrado'}), 404
        
        status_anterior = response.data[0]['status']
        now = time.strftime('%d/%m/%Y %H:%M:%S')
        
        # Atualizar status
        supabase.table('pedidos').update({
            'status': novo_status,
            'data_finalizacao': now if novo_status in ['Entregue', 'Cancelado'] else None
        }).eq('id', pedido_id).execute()
        
        # Registrar no histórico
        supabase.table('historico').insert({
            'pedido_id': pedido_id,
            'status': novo_status,
            'data': now,
            'observacoes': f'Status alterado de {status_anterior} para {novo_status}'
        }).execute()
        
        return jsonify({
            'message': 'status atualizado',
            'pedido_id': pedido_id,
            'status_novo': novo_status,
            'movido_para_historico': novo_status in ['Entregue', 'Cancelado']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pedidos/<int:pedido_id>', methods=['GET'])
def get_pedido(pedido_id):
    try:
        response = supabase.table('pedidos').select('*').eq('id', pedido_id).execute()
        
        if not response.data:
            return jsonify({'error': 'pedido não encontrado'}), 404
        
        pedido_data = response.data[0]
        
        # Buscar produtos
        produtos_response = supabase.table('pedido_produtos').select(
            'produto_id'
        ).eq('pedido_id', pedido_id).execute()
        
        produtos = []
        total = 0
        
        for item in produtos_response.data:
            prod_response = supabase.table('produtos').select('*').eq(
                'id', item['produto_id']
            ).execute()
            
            if prod_response.data:
                prod = prod_response.data[0]
                produtos.append({
                    'id': prod['id'],
                    'nome': prod['nome'],
                    'preco': prod['preco']
                })
                total += prod['preco']
        
        # Buscar histórico
        historico_response = supabase.table('historico').select('*').eq(
            'pedido_id', pedido_id
        ).execute()
        
        historico = historico_response.data if historico_response.data else []
        
        return jsonify({
            'id': pedido_data['id'],
            'cliente': pedido_data['cliente'],
            'status': pedido_data['status'],
            'total': total,
            'produtos': produtos,
            'historico': historico,
            'tipo': 'ativo' if pedido_data['status'] not in ['Entregue', 'Cancelado'] else 'finalizado',
            'data_criacao': pedido_data['data_criacao'],
            'data_finalizacao': pedido_data['data_finalizacao']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pedidos/historico', methods=['GET'])
def get_historico():
    try:
        response = supabase.table('pedidos').select('*').in_(
            'status', ['Entregue', 'Cancelado']
        ).execute()
        
        historico = []
        
        for pedido in response.data:
            # Contar produtos
            prods = supabase.table('pedido_produtos').select('*').eq(
                'pedido_id', pedido['id']
            ).execute()
            
            historico.append({
                'id': pedido['id'],
                'cliente': pedido['cliente'],
                'status': pedido['status'],
                'data_criacao': pedido['data_criacao'],
                'data_finalizacao': pedido['data_finalizacao'],
                'quantidade_produtos': len(prods.data) if prods.data else 0,
                'dias_ativos': 1  # Calcular corretamente se necessário
            })
        
        return jsonify(historico)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/estatisticas', methods=['GET'])
def get_estatisticas():
    try:
        # Total de pedidos
        todos = supabase.table('pedidos').select('*').execute()
        total_pedidos = len(todos.data) if todos.data else 0
        
        # Pedidos por status
        ativos = supabase.table('pedidos').select('*').not_.in_(
            'status', ['Entregue', 'Cancelado']
        ).execute()
        
        entregues = supabase.table('pedidos').select('*').eq(
            'status', 'Entregue'
        ).execute()
        
        cancelados = supabase.table('pedidos').select('*').eq(
            'status', 'Cancelado'
        ).execute()
        
        # Calcular total vendido
        valor_total = 0
        if entregues.data:
            for pedido in entregues.data:
                produtos = supabase.table('pedido_produtos').select(
                    'produto_id'
                ).eq('pedido_id', pedido['id']).execute()
                
                for item in produtos.data:
                    prod = supabase.table('produtos').select('preco').eq(
                        'id', item['produto_id']
                    ).execute()
                    if prod.data:
                        valor_total += prod.data[0]['preco']
        
        return jsonify({
            'pedidos_ativos': len(ativos.data) if ativos.data else 0,
            'pedidos_finalizados': len(entregues.data) + len(cancelados.data) if entregues.data or cancelados.data else 0,
            'pedidos_entregues': len(entregues.data) if entregues.data else 0,
            'pedidos_cancelados': len(cancelados.data) if cancelados.data else 0,
            'total_pedidos': total_pedidos,
            'valor_total_vendido': valor_total,
            'taxa_entrega': (len(entregues.data) / max(total_pedidos, 1) * 100) if entregues.data else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    print('Order service rodando na porta 5000')
    app.run(port=5000, debug=True)
