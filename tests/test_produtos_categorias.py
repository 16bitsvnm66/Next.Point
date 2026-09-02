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

class TestGestorProdutos(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(":memory:")
        init_db(self.conn)
        self.produtos = GestorProdutos(self.conn)
        self.categorias = GestorCategorias(self.conn)
        self.cat_roupa = self.categorias.adicionar(Categoria(nome="Roupa"))

    def tearDown(self):
        self.conn.close()

    def _produto_exemplo(self, **overrides):
        dados = dict(nome="Polo Padel", tamanho="M", preco=29.90, stock=15,
                     categoria_id=self.cat_roupa.id, cor="Verde")
        dados.update(overrides)
        return self.produtos.adicionar(Produto(**dados))

    def test_preco_negativo_gera_erro(self):
        with self.assertRaises(DadosInvalidosError):
            Produto(nome="Boné", tamanho="Único", preco=-5)

    def test_adicionar_e_obter(self):
        produto = self._produto_exemplo()
        obtido = self.produtos.obter(produto.id)
        self.assertEqual(obtido.nome, "Polo Padel")
        self.assertEqual(obtido.categoria_nome, "Roupa")

    def test_obter_inexistente_gera_erro(self):
        with self.assertRaises(ProdutoNaoEncontradoError):
            self.produtos.obter(999)

    def test_listar_com_filtro_categoria(self):
        outra_cat = self.categorias.adicionar(Categoria(nome="Calçado"))
        self._produto_exemplo(nome="Camisola")
        self._produto_exemplo(nome="Sapatilhas", categoria_id=outra_cat.id)
        resultado = self.produtos.listar(categoria_id=self.cat_roupa.id)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].nome, "Camisola")

    def test_stock_baixo(self):
        self._produto_exemplo(nome="Produto A", stock=1)
        self._produto_exemplo(nome="Produto B", stock=50)
        baixos = [p.nome for p in self.produtos.produtos_stock_baixo(limite=3)]
        self.assertIn("Produto A", baixos)
        self.assertNotIn("Produto B", baixos)

    def test_remover_produto(self):
        produto = self._produto_exemplo()
        self.produtos.remover(produto.id)
        with self.assertRaises(ProdutoNaoEncontradoError):
            self.produtos.obter(produto.id)

class TestGestorClientes(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(":memory:")
        init_db(self.conn)
        self.gestor = GestorClientes(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_email_invalido_gera_erro(self):
        with self.assertRaises(DadosInvalidosError):
            Cliente(nome="Ana", email="sem-arroba")

    def test_obter_ou_criar_por_email_reaproveita_cliente(self):
        cliente1 = self.gestor.obter_ou_criar_por_email(
            Cliente(nome="Ana Silva", email="ana@exemplo.pt", telefone="911111111"))
        cliente2 = self.gestor.obter_ou_criar_por_email(
            Cliente(nome="Ana Silva Costa", email="ana@exemplo.pt", telefone="922222222"))
        self.assertEqual(cliente1.id, cliente2.id)
        self.assertEqual(self.gestor.obter(cliente1.id).telefone, "922222222")

    def test_obter_cliente_inexistente_gera_erro(self):
        with self.assertRaises(ClienteNaoEncontradoError):
            self.gestor.obter(999)


if __name__ == "__main__":
    unittest.main()