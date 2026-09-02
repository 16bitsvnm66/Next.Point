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
