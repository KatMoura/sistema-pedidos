from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from models import UsuarioFactory, Usuario

load_dotenv()

app = Flask(__name__)
CORS(app)

# Inicializar Supabase
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Criar tabela se não existir
def init_db():
    try:
        # Tenta fazer uma query simples para verificar se a tabela existe
        supabase.table('usuarios').select('*').limit(1).execute()
        print("Tabela 'usuarios' já existe")
    except Exception as e:
        print(f"Tabela 'usuarios' não existe ou erro: {e}")
        # A tabela será criada via dashboard do Supabase

@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    try:
        response = supabase.table('usuarios').select('*').execute()
        users = response.data if response.data else []
        return jsonify(users)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    
    if not nome or not email:
        return jsonify({'error': 'nome e email obrigatórios'}), 400
    
    try:
        # Verificar se email já existe
        existing = supabase.table('usuarios').select('*').eq('email', email).execute()
        if existing.data:
            return jsonify({'error': 'email já registrado'}), 400
        
        # Criar novo usuário
        response = supabase.table('usuarios').insert({
            'nome': nome,
            'email': email
        }).execute()
        
        usuario = response.data[0] if response.data else None
        return jsonify({
            'id': usuario['id'],
            'nome': usuario['nome'],
            'email': usuario['email']
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:user_id>', methods=['GET'])
def get_usuario(user_id):
    try:
        response = supabase.table('usuarios').select('*').eq('id', user_id).execute()
        
        if not response.data:
            return jsonify({'error': 'usuário não encontrado'}), 404
        
        usuario = response.data[0]
        return jsonify(usuario)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:user_id>', methods=['PUT'])
def atualizar_usuario(user_id):
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    
    if not nome or not email:
        return jsonify({'error': 'nome e email obrigatórios'}), 400
    
    try:
        response = supabase.table('usuarios').update({
            'nome': nome,
            'email': email
        }).eq('id', user_id).execute()
        
        if not response.data:
            return jsonify({'error': 'usuário não encontrado'}), 404
        
        usuario = response.data[0]
        return jsonify({
            'id': usuario['id'],
            'nome': usuario['nome'],
            'email': usuario['email']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/usuarios/<int:user_id>', methods=['DELETE'])
def apagar_usuario(user_id):
    try:
        response = supabase.table('usuarios').delete().eq('id', user_id).execute()
        
        if not response.data:
            return jsonify({'error': 'usuário não encontrado'}), 404
        
        return jsonify({'message': 'usuário removido'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(port=5001, debug=True)