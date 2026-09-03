"""
blueprints/loja.py
---------------------
Rotas do lado do Cliente: consulta do catálogo, ficha de produto,
carrinho de compras (guardado na sessão) e checkout.
"""

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for

from gestor import GestorCategorias, GestorClientes, GestorEncomendas, GestorProdutos
from models import Cliente, DadosInvalidosError, StockInsuficienteError

loja_bp = Blueprint("loja", __name__)


def _carrinho() -> dict:
    """Devolve o carrinho da sessão: {"produto_id_str": quantidade}."""
    return session.setdefault("carrinho", {})

def _itens_do_carrinho():
    """Junta o carrinho da sessão com os dados atuais dos produtos."""
    gestor_produtos = GestorProdutos(g.db)
    itens = []
    total = 0.0
    for produto_id_str, quantidade in _carrinho().items():
        try:
            produto = gestor_produtos.obter(int(produto_id_str))
        except Exception:
            continue
        subtotal = round(produto.preco * quantidade, 2)
        total += subtotal
        itens.append({"produto": produto, "quantidade": quantidade, "subtotal": subtotal})
    return itens, round(total, 2)

@loja_bp.route("/")
def catalogo():
    gestor_produtos = GestorProdutos(g.db)
    gestor_categorias = GestorCategorias(g.db)

    termo = request.args.get("q", "")
    categoria_id = request.args.get("categoria", type=int)
    tamanho = request.args.get("tamanho", "")

    produtos = gestor_produtos.listar(termo_pesquisa=termo, categoria_id=categoria_id, tamanho=tamanho)
    categorias = gestor_categorias.listar()
    todos_produtos = gestor_produtos.listar()
    tamanhos = sorted({p.tamanho for p in todos_produtos})

    return render_template("loja/catalogo.html", produtos=produtos, categorias=categorias,
                            tamanhos=tamanhos, termo=termo, categoria_id=categoria_id,
                            tamanho=tamanho, total_carrinho=len(_carrinho()))