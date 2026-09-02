"""Testes unitários para GestorEncomendas: criação, cancelamento e relatórios."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import get_connection, init_db
from gestor import GestorClientes, GestorEncomendas, GestorProdutos
from models import Cliente, Produto, StockInsuficienteError


class TestGestorEncomendas(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(":memory:")
        init_db(self.conn)
        self.produtos = GestorProdutos(self.conn)
        self.clientes = GestorClientes(self.conn)
        self.encomendas = GestorEncomendas(self.conn)

        self.p1 = self.produtos.adicionar(Produto(nome="T-shirt", tamanho="M", preco=20.0, stock=10))
        self.p2 = self.produtos.adicionar(Produto(nome="Calções", tamanho="L", preco=15.0, stock=5))
        self.cliente = self.clientes.adicionar(Cliente(nome="Filipe Gomes", email="filipe@exemplo.pt"))