import sqlite3

DB_PATH = 'orders.db'


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # tabela de produtos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL
    )
    ''')
    # tabela de pedidos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT NOT NULL,
        status TEXT NOT NULL,
        data_criacao TEXT,
        data_finalizacao TEXT
    )
    ''')
    # ligação de produtos a pedidos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pedido_produtos (
        pedido_id INTEGER,
        produto_id INTEGER,
        FOREIGN KEY(pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY(produto_id) REFERENCES produtos(id)
    )
    ''')
    # histórico de status
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        status TEXT,
        data TEXT,
        observacoes TEXT,
        FOREIGN KEY(pedido_id) REFERENCES pedidos(id)
    )
    ''')
    conn.commit()
    conn.close()
