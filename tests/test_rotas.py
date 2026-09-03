"""
Testes de integração às rotas Flask, usando o test client (sem
precisar de um browser real). Verificam que as páginas respondem e
que o fluxo catálogo -> carrinho -> checkout -> encomenda funciona.
"""

import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import criar_app, popular_dados_exemplo_se_vazio
from database import criar_ligacao_e_iniciar

class TestRotas(unittest.TestCase):
    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmpdir.name) / "teste.db"

        conn = criar_ligacao_e_iniciar(self.db_path)
        popular_dados_exemplo_se_vazio(conn)
        conn.close()

        self.app = criar_app(db_path=self.db_path)
        self.app.testing = True
        self.client = self.app.test_client()