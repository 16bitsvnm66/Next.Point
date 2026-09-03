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

@loja_bp.route("/produto/<int:produto_id>")
def ficha_produto(produto_id):
    gestor_produtos = GestorProdutos(g.db)
    produto = gestor_produtos.obter(produto_id)
    return render_template("loja/produto.html", produto=produto, total_carrinho=len(_carrinho()))


@loja_bp.route("/carrinho/adicionar/<int:produto_id>", methods=["POST"])
def adicionar_ao_carrinho(produto_id):
    quantidade = request.form.get("quantidade", 1, type=int)
    if quantidade < 1:
        quantidade = 1
    carrinho = _carrinho()
    chave = str(produto_id)
    carrinho[chave] = carrinho.get(chave, 0) + quantidade
    session.modified = True
    flash("Produto adicionado ao carrinho.", "success")
    return redirect(request.referrer or url_for("loja.catalogo"))

@loja_bp.route("/carrinho")
def ver_carrinho():
    itens, total = _itens_do_carrinho()
    return render_template("loja/carrinho.html", itens=itens, total=total)


@loja_bp.route("/carrinho/atualizar/<int:produto_id>", methods=["POST"])
def atualizar_carrinho(produto_id):
    quantidade = request.form.get("quantidade", 1, type=int)
    carrinho = _carrinho()
    chave = str(produto_id)
    if quantidade <= 0:
        carrinho.pop(chave, None)
    else:
        carrinho[chave] = quantidade
    session.modified = True
    return redirect(url_for("loja.ver_carrinho"))


@loja_bp.route("/carrinho/remover/<int:produto_id>", methods=["POST"])
def remover_do_carrinho(produto_id):
    _carrinho().pop(str(produto_id), None)
    session.modified = True
    flash("Produto removido do carrinho.", "info")
    return redirect(url_for("loja.ver_carrinho"))