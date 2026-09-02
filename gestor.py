"""
gestor.py
-----------
Camada de lógica de negócio ("service layer"). Cada classe recebe uma
ligação sqlite3 já aberta (ver database.py) e expõe métodos de alto
nível para as rotas Flask usarem, sem que estas precisem de saber SQL.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from models import (
    Categoria,
    CategoriaNaoEncontradaError,
    Cliente,
    ClienteNaoEncontradoError,
    Encomenda,
    EncomendaNaoEncontradaError,
    ItemEncomenda,
    Produto,
    ProdutoNaoEncontradoError,
    StockInsuficienteError,
)

class GestorCategorias:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def adicionar(self, categoria: Categoria) -> Categoria:
        cur = self.conn.execute("INSERT INTO categorias (nome) VALUES (?)", (categoria.nome,))
        self.conn.commit()
        categoria.id = cur.lastrowid
        return categoria

    def actualizar(self, categoria: Categoria) -> None:
        cur = self.conn.execute("UPDATE categorias SET nome=? WHERE id=?",
                                 (categoria.nome, categoria.id))
        self.conn.commit()
        if cur.rowcount == 0:
            raise CategoriaNaoEncontradaError(categoria.id)

    def remover(self, categoria_id: int) -> None:
        cur = self.conn.execute("DELETE FROM categorias WHERE id=?", (categoria_id,))
        self.conn.commit()
        if cur.rowcount == 0:
            raise CategoriaNaoEncontradaError(categoria_id)

    def obter(self, categoria_id: int) -> Categoria:
        row = self.conn.execute("SELECT * FROM categorias WHERE id=?", (categoria_id,)).fetchone()
        if row is None:
            raise CategoriaNaoEncontradaError(categoria_id)
        return Categoria(id=row["id"], nome=row["nome"])

    def listar(self) -> List[Categoria]:
        rows = self.conn.execute("SELECT * FROM categorias ORDER BY nome").fetchall()
        return [Categoria(id=r["id"], nome=r["nome"]) for r in rows]
