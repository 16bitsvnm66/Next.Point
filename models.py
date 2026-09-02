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


# --------------------------------------------------------------------------
# Entidades
# --------------------------------------------------------------------------

@dataclass
class Categoria:
    nome: str
    id: Optional[int] = None

    def __post_init__(self):
        if not self.nome.strip():
            raise DadosInvalidosError("O nome da categoria não pode estar vazio.")


@dataclass
class Produto:
    nome: str
    tamanho: str
    preco: float
    categoria_id: Optional[int] = None
    categoria_nome: str = ""   # apenas para exibição (join), não é gravado
    descricao: str = ""
    cor: str = ""
    stock: int = 0
    imagem_url: str = ""
    id: Optional[int] = None

    def __post_init__(self):
        if not self.nome.strip():
            raise DadosInvalidosError("O nome do produto não pode estar vazio.")
        if self.preco < 0:
            raise DadosInvalidosError("O preço não pode ser negativo.")
        if self.stock < 0:
            raise DadosInvalidosError("O stock não pode ser negativo.")

    @property
    def em_rutura(self) -> bool:
        return self.stock <= 3


@dataclass
class Cliente:
    nome: str
    email: str
    telefone: str = ""
    id: Optional[int] = None

    def __post_init__(self):
        if not self.nome.strip():
            raise DadosInvalidosError("O nome do cliente não pode estar vazio.")
        if "@" not in self.email:
            raise DadosInvalidosError("Indica um email válido.")


@dataclass
class ItemEncomenda:
    produto_id: int
    quantidade: int
    preco_unitario: float
    nome_produto: str = ""
    id: Optional[int] = None
    encomenda_id: Optional[int] = None

    def __post_init__(self):
        if self.quantidade <= 0:
            raise DadosInvalidosError("A quantidade tem de ser maior que zero.")

    @property
    def subtotal(self) -> float:
        return round(self.quantidade * self.preco_unitario, 2)


@dataclass
class Encomenda:
    itens: list = field(default_factory=list)   # list[ItemEncomenda]
    cliente_id: Optional[int] = None
    data_criacao: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))
    estado: str = "pendente"
    observacoes: str = ""
    id: Optional[int] = None

    @property
    def total(self) -> float:
        return round(sum(item.subtotal for item in self.itens), 2)