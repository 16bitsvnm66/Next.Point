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
        
class GestorClientes:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def adicionar(self, cliente: Cliente) -> Cliente:
        cur = self.conn.execute(
            "INSERT INTO clientes (nome, email, telefone) VALUES (?, ?, ?)",
            (cliente.nome, cliente.email, cliente.telefone),
        )
        self.conn.commit()
        cliente.id = cur.lastrowid
        return cliente

    def obter_ou_criar_por_email(self, cliente: Cliente) -> Cliente:
        """Usado no checkout: reaproveita o cliente se o email já existir."""
        row = self.conn.execute("SELECT * FROM clientes WHERE email=?", (cliente.email,)).fetchone()
        if row:
            existente = Cliente(id=row["id"], nome=row["nome"], email=row["email"],
                                 telefone=row["telefone"] or "")
            existente.nome = cliente.nome
            existente.telefone = cliente.telefone
            self.actualizar(existente)
            return existente
        return self.adicionar(cliente)

    def actualizar(self, cliente: Cliente) -> None:
        cur = self.conn.execute(
            "UPDATE clientes SET nome=?, email=?, telefone=? WHERE id=?",
            (cliente.nome, cliente.email, cliente.telefone, cliente.id),
        )
        self.conn.commit()
        if cur.rowcount == 0:
            raise ClienteNaoEncontradoError(cliente.id)

    def remover(self, cliente_id: int) -> None:
        cur = self.conn.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
        self.conn.commit()
        if cur.rowcount == 0:
            raise ClienteNaoEncontradoError(cliente_id)

    def obter(self, cliente_id: int) -> Cliente:
        row = self.conn.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,)).fetchone()
        if row is None:
            raise ClienteNaoEncontradoError(cliente_id)
        return Cliente(id=row["id"], nome=row["nome"], email=row["email"],
                        telefone=row["telefone"] or "")

    def listar(self, termo_pesquisa: str = "") -> List[Cliente]:
        query = "SELECT * FROM clientes WHERE 1=1"
        params = []
        if termo_pesquisa:
            query += " AND nome LIKE ?"
            params.append(f"%{termo_pesquisa}%")
        query += " ORDER BY nome"
        rows = self.conn.execute(query, params).fetchall()
        return [Cliente(id=r["id"], nome=r["nome"], email=r["email"],
                         telefone=r["telefone"] or "") for r in rows]
        
class GestorEncomendas:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.gestor_produtos = GestorProdutos(conn)

    def criar_encomenda(self, itens: List[tuple], cliente_id: Optional[int] = None,
                         observacoes: str = "") -> Encomenda:
        """
        itens: lista de tuplos (produto_id, quantidade).
        Valida stock, regista a encomenda e actualiza o stock, tudo numa
        única transacção (se algo falhar, nada é gravado).
        """
        if not itens:
            raise ValueError("Uma encomenda tem de ter pelo menos um item.")

        itens_encomenda: List[ItemEncomenda] = []
        try:
            for produto_id, quantidade in itens:
                produto = self.gestor_produtos.obter(produto_id)
                if produto.stock < quantidade:
                    raise StockInsuficienteError(produto.nome, quantidade, produto.stock)
                itens_encomenda.append(ItemEncomenda(
                    produto_id=produto_id, quantidade=quantidade,
                    preco_unitario=produto.preco, nome_produto=produto.nome,
                ))

            encomenda = Encomenda(itens=itens_encomenda, cliente_id=cliente_id,
                                   observacoes=observacoes,
                                   data_criacao=datetime.now().strftime("%Y-%m-%d %H:%M"))

            cur = self.conn.execute(
                """INSERT INTO encomendas (cliente_id, estado, data_criacao, total, observacoes)
                   VALUES (?, ?, ?, ?, ?)""",
                (encomenda.cliente_id, encomenda.estado, encomenda.data_criacao,
                 encomenda.total, encomenda.observacoes),
            )
            encomenda.id = cur.lastrowid

            for item in itens_encomenda:
                self.conn.execute(
                    """INSERT INTO itens_encomenda (encomenda_id, produto_id, quantidade, preco_unitario)
                       VALUES (?, ?, ?, ?)""",
                    (encomenda.id, item.produto_id, item.quantidade, item.preco_unitario),
                )
                self.conn.execute(
                    "UPDATE produtos SET stock = stock - ? WHERE id = ?",
                    (item.quantidade, item.produto_id),
                )
            self.conn.commit()
            return encomenda
        except Exception:
            self.conn.rollback()
            raise

    def actualizar_estado(self, encomenda_id: int, novo_estado: str) -> None:
        cur = self.conn.execute("UPDATE encomendas SET estado=? WHERE id=?",
                                 (novo_estado, encomenda_id))
        self.conn.commit()
        if cur.rowcount == 0:
            raise EncomendaNaoEncontradaError(encomenda_id)

    def cancelar(self, encomenda_id: int) -> None:
        """Repõe o stock dos produtos e marca a encomenda como cancelada."""
        itens = self.conn.execute(
            "SELECT produto_id, quantidade FROM itens_encomenda WHERE encomenda_id=?",
            (encomenda_id,),
        ).fetchall()
        if not itens:
            raise EncomendaNaoEncontradaError(encomenda_id)
        try:
            for item in itens:
                self.conn.execute(
                    "UPDATE produtos SET stock = stock + ? WHERE id = ?",
                    (item["quantidade"], item["produto_id"]),
                )
            self.conn.execute("UPDATE encomendas SET estado='cancelada' WHERE id=?", (encomenda_id,))
            self.conn.commit()
        except Exception:
            self.conn.rollback()
            raise

    def obter(self, encomenda_id: int) -> dict:
        row = self.conn.execute(
            """SELECT encomendas.*, COALESCE(clientes.nome, 'Cliente ocasional') AS cliente_nome,
                      clientes.email AS cliente_email
               FROM encomendas LEFT JOIN clientes ON clientes.id = encomendas.cliente_id
               WHERE encomendas.id=?""", (encomenda_id,)
        ).fetchone()
        if row is None:
            raise EncomendaNaoEncontradaError(encomenda_id)
        return dict(row)

    def listar(self, estado: str = "") -> List[dict]:
        query = """SELECT encomendas.*, COALESCE(clientes.nome, 'Cliente ocasional') AS cliente_nome
                   FROM encomendas LEFT JOIN clientes ON clientes.id = encomendas.cliente_id
                   WHERE 1=1"""
        params = []
        if estado:
            query += " AND encomendas.estado = ?"
            params.append(estado)
        query += " ORDER BY encomendas.data_criacao DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]

    def itens_da_encomenda(self, encomenda_id: int) -> List[dict]:
        rows = self.conn.execute(
            """SELECT itens_encomenda.quantidade, itens_encomenda.preco_unitario,
                      produtos.nome AS nome_produto, produtos.id AS produto_id
               FROM itens_encomenda
               JOIN produtos ON produtos.id = itens_encomenda.produto_id
               WHERE itens_encomenda.encomenda_id = ?""",
            (encomenda_id,),
        ).fetchall()
        return [dict(r) for r in rows]

    def relatorio_receita_total(self) -> float:
        row = self.conn.execute(
            "SELECT COALESCE(SUM(total), 0) AS total FROM encomendas WHERE estado != 'cancelada'"
        ).fetchone()
        return round(row["total"], 2)

    def relatorio_produtos_mais_vendidos(self, limite: int = 5) -> List[dict]:
        rows = self.conn.execute(
            """SELECT produtos.nome, SUM(itens_encomenda.quantidade) AS total_vendido
               FROM itens_encomenda
               JOIN encomendas ON encomendas.id = itens_encomenda.encomenda_id
               JOIN produtos ON produtos.id = itens_encomenda.produto_id
               WHERE encomendas.estado != 'cancelada'
               GROUP BY produtos.id
               ORDER BY total_vendido DESC
               LIMIT ?""",
            (limite,),
        ).fetchall()
        return [dict(r) for r in rows]