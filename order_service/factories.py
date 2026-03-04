import sqlite3
from models import Pedido, Produto
from db import DB_PATH


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


class ProdutoFactory:
    @staticmethod
    def create(nome: str, preco: float) -> Produto:
        return Produto(nome, preco)

    @staticmethod
    def from_db(produto_id: int) -> Produto:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, nome, preco FROM produtos WHERE id=?', (produto_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return Produto(row['nome'], row['preco'], id=row['id'])


class PedidoFactory:
    @staticmethod
    def create(cliente: str, produtos: list[Produto]) -> Pedido:
        pedido = Pedido(cliente)
        for p in produtos:
            pedido.adicionar_produto(p)
        return pedido

    @staticmethod
    def from_db(pedido_id: int) -> Pedido:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, cliente, status FROM pedidos WHERE id=?', (pedido_id,))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        pedido = Pedido(row['cliente'], id=row['id'])
        pedido._status = row['status']
        cursor.execute('SELECT produto_id FROM pedido_produtos WHERE pedido_id=?', (pedido_id,))
        for prod in cursor.fetchall():
            produto = ProdutoFactory.from_db(prod['produto_id'])
            if produto:
                pedido.adicionar_produto(produto)
        conn.close()
        return pedido
