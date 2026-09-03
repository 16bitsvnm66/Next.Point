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
    
    def tearDown(self):
            self.conn.close()
    
    def test_criar_encomenda_calcula_total_correcto(self):
            encomenda = self.encomendas.criar_encomenda(
                itens=[(self.p1.id, 2), (self.p2.id, 1)], cliente_id=self.cliente.id)
            self.assertEqual(encomenda.total, 55.0)  # 2*20 + 1*15
    
    def test_criar_encomenda_actualiza_stock(self):
            self.encomendas.criar_encomenda(itens=[(self.p1.id, 3)], cliente_id=self.cliente.id)
            self.assertEqual(self.produtos.obter(self.p1.id).stock, 7)
    
    def test_stock_insuficiente_nao_grava_nada(self):
            with self.assertRaises(StockInsuficienteError):
                self.encomendas.criar_encomenda(itens=[(self.p2.id, 999)], cliente_id=self.cliente.id)
            self.assertEqual(self.produtos.obter(self.p2.id).stock, 5)
            self.assertEqual(len(self.encomendas.listar()), 0)
    def test_encomenda_sem_itens_gera_erro(self):
            with self.assertRaises(ValueError):
                self.encomendas.criar_encomenda(itens=[], cliente_id=self.cliente.id)
    
    def test_cancelar_encomenda_repoe_stock(self):
            encomenda = self.encomendas.criar_encomenda(itens=[(self.p1.id, 4)], cliente_id=self.cliente.id)
            self.encomendas.cancelar(encomenda.id)
            self.assertEqual(self.produtos.obter(self.p1.id).stock, 10)
            self.assertEqual(self.encomendas.obter(encomenda.id)["estado"], "cancelada")
    
    def test_actualizar_estado(self):
            encomenda = self.encomendas.criar_encomenda(itens=[(self.p1.id, 1)], cliente_id=self.cliente.id)
            self.encomendas.actualizar_estado(encomenda.id, "confirmada")
            self.assertEqual(self.encomendas.obter(encomenda.id)["estado"], "confirmada")
    
    def test_relatorio_receita_ignora_canceladas(self):
            v1 = self.encomendas.criar_encomenda(itens=[(self.p1.id, 1)], cliente_id=self.cliente.id)
            self.encomendas.criar_encomenda(itens=[(self.p2.id, 1)], cliente_id=self.cliente.id)
            self.encomendas.cancelar(v1.id)
            self.assertEqual(self.encomendas.relatorio_receita_total(), 15.0)
    
    def test_relatorio_produtos_mais_vendidos(self):
            self.encomendas.criar_encomenda(itens=[(self.p1.id, 5)], cliente_id=self.cliente.id)
            self.encomendas.criar_encomenda(itens=[(self.p2.id, 1)], cliente_id=self.cliente.id)
            ranking = self.encomendas.relatorio_produtos_mais_vendidos(limite=1)
            self.assertEqual(ranking[0]["nome"], "T-shirt")
            self.assertEqual(ranking[0]["total_vendido"], 5)
    
    
if __name__ == "__main__":
    unittest.main()
    