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