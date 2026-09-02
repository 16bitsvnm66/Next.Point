"""
database.py
-------------
Camada de acesso à base de dados. Abre ligações SQLite e garante que
o esquema (tabelas) existe.
"""

import sqlite3
from pathlib import Path

DB_PATH_DEFAULT = Path(__file__).parent / "next_point.db"

ESQUEMA_SQL = """
CREATE TABLE IF NOT EXISTS categorias (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nome    TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS produtos (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    nome          TEXT NOT NULL,
    descricao     TEXT,
    categoria_id  INTEGER,
    tamanho       TEXT NOT NULL,
    cor           TEXT,
    preco         REAL NOT NULL CHECK (preco >= 0),
    stock         INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    imagem_url    TEXT,
    FOREIGN KEY (categoria_id) REFERENCES categorias (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS clientes (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT NOT NULL,
    email     TEXT NOT NULL,
    telefone  TEXT
);

CREATE TABLE IF NOT EXISTS encomendas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id     INTEGER,
    estado         TEXT NOT NULL DEFAULT 'pendente',
    data_criacao   TEXT NOT NULL,
    total          REAL NOT NULL DEFAULT 0,
    observacoes    TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS itens_encomenda (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    encomenda_id    INTEGER NOT NULL,
    produto_id      INTEGER NOT NULL,
    quantidade      INTEGER NOT NULL CHECK (quantidade > 0),
    preco_unitario  REAL NOT NULL CHECK (preco_unitario >= 0),
    FOREIGN KEY (encomenda_id) REFERENCES encomendas (id) ON DELETE CASCADE,
    FOREIGN KEY (produto_id) REFERENCES produtos (id)
);
"""

ESTADOS_ENCOMENDA = ["pendente", "confirmada", "enviada", "concluida", "cancelada"]

def get_connection(db_path=DB_PATH_DEFAULT) -> sqlite3.Connection:
    """Abre (ou cria) a base de dados e devolve uma ligação pronta a usar."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Cria as tabelas caso ainda não existam."""
    conn.executescript(ESQUEMA_SQL)
    conn.commit()


def criar_ligacao_e_iniciar(db_path=DB_PATH_DEFAULT) -> sqlite3.Connection:
    """Atalho: abre a ligação e garante que o esquema está criado."""
    conn = get_connection(db_path)
    init_db(conn)
    return conn

