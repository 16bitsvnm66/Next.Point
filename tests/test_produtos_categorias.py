"""Testes unitários para GestorProdutos, GestorCategorias e GestorClientes."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import get_connection, init_db
from gestor import GestorCategorias, GestorClientes, GestorProdutos
from models import (
    CategoriaNaoEncontradaError, Categoria, Cliente, ClienteNaoEncontradoError,
    DadosInvalidosError, Produto, ProdutoNaoEncontradoError,
)

class TestGestorCategorias(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(":memory:")
        init_db(self.conn)
        self.gestor = GestorCategorias(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_adicionar_e_listar(self):
        self.gestor.adicionar(Categoria(nome="Roupa"))
        self.gestor.adicionar(Categoria(nome="Calçado"))
        nomes = [c.nome for c in self.gestor.listar()]
        self.assertEqual(nomes, ["Calçado", "Roupa"])  # ordenado por nome

    def test_remover_categoria_inexistente_gera_erro(self):
        with self.assertRaises(CategoriaNaoEncontradaError):
            self.gestor.remover(999)