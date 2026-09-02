"""
models.py
-----------
Classes de dados (POO) que representam as entidades do Next Point.
Não sabem nada sobre SQL — isso fica na camada gestor.py.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

# --------------------------------------------------------------------------
# Exceções de negócio
# --------------------------------------------------------------------------

class NextPointError(Exception):
    """Classe base para todas as exceções específicas do domínio."""


class EntidadeNaoEncontradaError(NextPointError):
    """Classe base comum a todos os erros de 'X não encontrado', para
    permitir um único errorhandler Flask (ver app.py) que devolve 404."""


class ProdutoNaoEncontradoError(EntidadeNaoEncontradaError):
    def __init__(self, produto_id: int):
        super().__init__(f"Produto com id {produto_id} não encontrado.")
        self.produto_id = produto_id


class CategoriaNaoEncontradaError(EntidadeNaoEncontradaError):
    def __init__(self, categoria_id: int):
        super().__init__(f"Categoria com id {categoria_id} não encontrada.")
        self.categoria_id = categoria_id


class ClienteNaoEncontradoError(EntidadeNaoEncontradaError):
    def __init__(self, cliente_id: int):
        super().__init__(f"Cliente com id {cliente_id} não encontrado.")
        self.cliente_id = cliente_id


class EncomendaNaoEncontradaError(EntidadeNaoEncontradaError):
    def __init__(self, encomenda_id: int):
        super().__init__(f"Encomenda com id {encomenda_id} não encontrada.")
        self.encomenda_id = encomenda_id


class StockInsuficienteError(NextPointError):
    def __init__(self, produto_nome: str, pedido: int, disponivel: int):
        super().__init__(
            f"Stock insuficiente para '{produto_nome}': "
            f"pedido {pedido}, disponível {disponivel}."
        )
        self.produto_nome = produto_nome
        self.pedido = pedido
        self.disponivel = disponivel


class DadosInvalidosError(NextPointError):
    """Levantada quando os dados fornecidos falham a validação."""
