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

class GestorProdutos:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def adicionar(self, produto: Produto) -> Produto:
        cur = self.conn.execute(
            """INSERT INTO produtos (nome, descricao, categoria_id, tamanho, cor,
                                      preco, stock, imagem_url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (produto.nome, produto.descricao, produto.categoria_id,
             produto.tamanho, produto.cor, produto.preco, produto.stock, produto.imagem_url),
        )
        self.conn.commit()
        produto.id = cur.lastrowid
        return produto

    def actualizar(self, produto: Produto) -> None:
        cur = self.conn.execute(
            """UPDATE produtos SET nome=?, descricao=?, categoria_id=?, tamanho=?,
               cor=?, preco=?, stock=?, imagem_url=? WHERE id=?""",
            (produto.nome, produto.descricao, produto.categoria_id,
             produto.tamanho, produto.cor, produto.preco, produto.stock,
             produto.imagem_url, produto.id),
        )
        self.conn.commit()
        if cur.rowcount == 0:
            raise ProdutoNaoEncontradoError(produto.id)

    def remover(self, produto_id: int) -> None:
        cur = self.conn.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
        self.conn.commit()
        if cur.rowcount == 0:
            raise ProdutoNaoEncontradoError(produto_id)

    def obter(self, produto_id: int) -> Produto:
        row = self.conn.execute(
            """SELECT produtos.*, categorias.nome AS categoria_nome
               FROM produtos LEFT JOIN categorias ON categorias.id = produtos.categoria_id
               WHERE produtos.id=?""", (produto_id,)
        ).fetchone()
        if row is None:
            raise ProdutoNaoEncontradoError(produto_id)
        return self._linha_para_produto(row)

    def listar(self, termo_pesquisa: str = "", categoria_id: Optional[int] = None,
               tamanho: str = "", apenas_com_stock: bool = False) -> List[Produto]:
        query = """SELECT produtos.*, categorias.nome AS categoria_nome
                   FROM produtos LEFT JOIN categorias ON categorias.id = produtos.categoria_id
                   WHERE 1=1"""
        params = []
        if termo_pesquisa:
            query += " AND produtos.nome LIKE ?"
            params.append(f"%{termo_pesquisa}%")
        if categoria_id:
            query += " AND produtos.categoria_id = ?"
            params.append(categoria_id)
        if tamanho:
            query += " AND produtos.tamanho = ?"
            params.append(tamanho)
        if apenas_com_stock:
            query += " AND produtos.stock > 0"
        query += " ORDER BY produtos.nome"
        rows = self.conn.execute(query, params).fetchall()
        return [self._linha_para_produto(r) for r in rows]

    def produtos_stock_baixo(self, limite: int = 3) -> List[Produto]:
        rows = self.conn.execute(
            """SELECT produtos.*, categorias.nome AS categoria_nome
               FROM produtos LEFT JOIN categorias ON categorias.id = produtos.categoria_id
               WHERE produtos.stock <= ? ORDER BY produtos.stock""", (limite,)
        ).fetchall()
        return [self._linha_para_produto(r) for r in rows]

    @staticmethod
    def _linha_para_produto(row: sqlite3.Row) -> Produto:
        return Produto(
            id=row["id"], nome=row["nome"], descricao=row["descricao"] or "",
            categoria_id=row["categoria_id"], categoria_nome=row["categoria_nome"] or "Sem categoria",
            tamanho=row["tamanho"], cor=row["cor"] or "",
            preco=row["preco"], stock=row["stock"], imagem_url=row["imagem_url"] or "",
        )