from flask import Flask, request, jsonify
import sqlite3
from models import UsuarioFactory, init_db, Usuario

app = Flask(__name__)
init_db()

DB_PATH = 'users.db'

# helpers

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, email FROM usuarios')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)


@app.route('/api/usuarios', methods=['POST'])
def criar_usuario():
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    if not nome or not email:
        return jsonify({'error': 'nome e email obrigatórios'}), 400
    usuario = UsuarioFactory.create(nome, email)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO usuarios (nome, email) VALUES (?,?)', (usuario.nome, usuario.email))
        conn.commit()
        usuario.id = cursor.lastrowid
    except sqlite3.IntegrityError as e:
        conn.close()
        return jsonify({'error': str(e)}), 400
    conn.close()
    return jsonify({'id': usuario.id, 'nome': usuario.nome, 'email': usuario.email}), 201


@app.route('/api/usuarios/<int:user_id>', methods=['GET'])
def get_usuario(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, nome, email FROM usuarios WHERE id=?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'usuário não encontrado'}), 404
    return jsonify(dict(row))


@app.route('/api/usuarios/<int:user_id>', methods=['PUT'])
def atualizar_usuario(user_id):
    data = request.json
    nome = data.get('nome')
    email = data.get('email')
    if not nome or not email:
        return jsonify({'error': 'nome e email obrigatórios'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE usuarios SET nome=?, email=? WHERE id=?', (nome, email, user_id))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'usuário não encontrado'}), 404
    conn.commit()
    conn.close()
    return jsonify({'id': user_id, 'nome': nome, 'email': email})


@app.route('/api/usuarios/<int:user_id>', methods=['DELETE'])
def apagar_usuario(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usuarios WHERE id=?', (user_id,))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'usuário não encontrado'}), 404
    conn.commit()
    conn.close()
    return jsonify({'message': 'usuário removido'})


if __name__ == '__main__':
    app.run(port=5001, debug=True)
