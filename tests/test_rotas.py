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

    def tearDown(self):
        self._tmpdir.cleanup()

    def test_catalogo_responde(self):
        resposta = self.client.get("/")
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Next Point".encode(), resposta.data)

    def test_ficha_produto_responde(self):
        resposta = self.client.get("/produto/1")
        self.assertEqual(resposta.status_code, 200)

    def test_produto_inexistente_devolve_404_tratado(self):
        resposta = self.client.get("/produto/9999")
        self.assertEqual(resposta.status_code, 404)
        self.assertIn("não encontrado".encode(), resposta.data)

    def test_admin_dashboard_responde(self):
        resposta = self.client.get("/admin/")
        self.assertEqual(resposta.status_code, 200)

    def test_admin_produtos_responde(self):
        resposta = self.client.get("/admin/produtos")
        self.assertEqual(resposta.status_code, 200)

    def test_fluxo_completo_carrinho_checkout(self):
        resposta = self.client.post("/carrinho/adicionar/1", data={"quantidade": "2"},
                                     follow_redirects=True)
        self.assertEqual(resposta.status_code, 200)

        resposta = self.client.get("/carrinho")
        self.assertEqual(resposta.status_code, 200)

        resposta = self.client.post("/checkout", data={
            "nome": "Cliente Teste", "email": "teste@exemplo.pt", "telefone": "911111111",
        }, follow_redirects=True)
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("Obrigado".encode(), resposta.data)

        resposta_admin = self.client.get("/admin/encomendas")
        self.assertIn("Cliente Teste".encode(), resposta_admin.data)

    def test_criar_produto_com_upload_de_imagem(self):
        import base64
        png_1x1 = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk"
            "+A8AAQUBAScY42YAAAAASUVORK5CYII="
        )
        resposta = self.client.post("/admin/produtos/novo", data={
            "nome": "Produto Com Foto", "descricao": "teste", "categoria_id": "1",
            "tamanho": "M", "cor": "Preto", "preco": "10", "stock": "5",
            "imagem": (io.BytesIO(png_1x1), "foto.png"),
        }, content_type="multipart/form-data", follow_redirects=True)
        self.assertEqual(resposta.status_code, 200)

        resposta_catalogo = self.client.get("/?q=Produto Com Foto")
        self.assertIn("Produto Com Foto".encode(), resposta_catalogo.data)
    
if __name__ == "__main__":
    unittest.main()
    
        
   