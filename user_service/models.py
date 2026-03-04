import sqlite3
from dataclasses import dataclass

DB_PATH = 'users.db'

@dataclass
class Usuario:
    id: int = None
    nome: str = ''
    email: str = ''


class UsuarioFactory:
    @staticmethod
    def create(nome: str, email: str) -> Usuario:
        """Factory method para criar uma instância de Usuario.
        Pode ser estendido no futuro para adicionar validações ou campos gerados.
        """
        return Usuario(None, nome, email)


def init_db():
    """Cria a tabela de usuários se não existir."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
    ''')
    conn.commit()
    conn.close()
