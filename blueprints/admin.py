"""
blueprints/admin.py
----------------------
Rotas da área de administração da loja: gestão de produtos,
categorias, clientes, encomendas e relatórios.
"""

import csv
import io
import os
import uuid

from flask import Blueprint, Response, current_app, flash, g, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

from database import ESTADOS_ENCOMENDA
from gestor import GestorCategorias, GestorClientes, GestorEncomendas, GestorProdutos
from models import Categoria, Cliente, DadosInvalidosError, NextPointError, Produto

admin_bp = Blueprint("admin", __name__)

EXTENSOES_PERMITIDAS = {"png", "jpg", "jpeg", "webp", "gif"}

def _extensao_valida(nome_ficheiro):
    return "." in nome_ficheiro and nome_ficheiro.rsplit(".", 1)[1].lower() in EXTENSOES_PERMITIDAS


def _guardar_imagem(ficheiro):
    """Guarda o ficheiro enviado em static/uploads com um nome único.
    Devolve o nome do ficheiro guardado, ou None se não houver imagem válida."""
    if not ficheiro or not ficheiro.filename or not _extensao_valida(ficheiro.filename):
        return None
    extensao = secure_filename(ficheiro.filename).rsplit(".", 1)[1].lower()
    nome_unico = f"{uuid.uuid4().hex}.{extensao}"
    pasta_uploads = os.path.join(current_app.static_folder, "uploads")
    os.makedirs(pasta_uploads, exist_ok=True)
    ficheiro.save(os.path.join(pasta_uploads, nome_unico))
    return nome_unico

@admin_bp.route("/")
def dashboard():
    gestor_produtos = GestorProdutos(g.db)
    gestor_encomendas = GestorEncomendas(g.db)
    resumo = {
        "total_produtos": len(gestor_produtos.listar()),
        "stock_baixo": len(gestor_produtos.produtos_stock_baixo()),
        "encomendas_pendentes": len(gestor_encomendas.listar(estado="pendente")),
        "receita_total": gestor_encomendas.relatorio_receita_total(),
    }
    return render_template("admin/dashboard.html", resumo=resumo)

    
    # ---------------------------------------------------------------- Produtos --
@admin_bp.route("/produtos")
def produtos():
    gestor_produtos = GestorProdutos(g.db)
    gestor_categorias = GestorCategorias(g.db)
    termo = request.args.get("q", "")
    return render_template("admin/produtos.html", produtos=gestor_produtos.listar(termo_pesquisa=termo),
                            categorias=gestor_categorias.listar(), termo=termo)


@admin_bp.route("/produtos/novo", methods=["POST"])
def criar_produto():
    try:
        produto = Produto(
            nome=request.form.get("nome", "").strip(),
            descricao=request.form.get("descricao", "").strip(),
            categoria_id=request.form.get("categoria_id", type=int),
            tamanho=request.form.get("tamanho", "").strip() or "Único",
            cor=request.form.get("cor", "").strip(),
            preco=float(request.form.get("preco", 0) or 0),
            stock=int(request.form.get("stock", 0) or 0),
            imagem_url=_guardar_imagem(request.files.get("imagem")) or "",
        )
        GestorProdutos(g.db).adicionar(produto)
        flash("Produto criado com sucesso.", "success")
    except (DadosInvalidosError, ValueError) as erro:
        flash(f"Não foi possível criar o produto: {erro}", "danger")
    return redirect(url_for("admin.produtos"))

@admin_bp.route("/produtos/<int:produto_id>/editar", methods=["POST"])
def editar_produto(produto_id):
    try:
        gestor_produtos = GestorProdutos(g.db)
        imagem_actual = gestor_produtos.obter(produto_id).imagem_url
        nova_imagem = _guardar_imagem(request.files.get("imagem"))

        produto = Produto(
            id=produto_id,
            nome=request.form.get("nome", "").strip(),
            descricao=request.form.get("descricao", "").strip(),
            categoria_id=request.form.get("categoria_id", type=int),
            tamanho=request.form.get("tamanho", "").strip() or "Único",
            cor=request.form.get("cor", "").strip(),
            preco=float(request.form.get("preco", 0) or 0),
            stock=int(request.form.get("stock", 0) or 0),
            imagem_url=nova_imagem or imagem_actual,
        )
        gestor_produtos.actualizar(produto)
        flash("Produto atualizado.", "success")
    except (DadosInvalidosError, ValueError, NextPointError) as erro:
        flash(f"Não foi possível atualizar o produto: {erro}", "danger")
    return redirect(url_for("admin.produtos"))

@admin_bp.route("/produtos/<int:produto_id>/remover", methods=["POST"])
def remover_produto(produto_id):
    try:
        GestorProdutos(g.db).remover(produto_id)
        flash("Produto removido.", "info")
    except NextPointError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("admin.produtos"))

# -------------------------------------------------------------- Categorias --
@admin_bp.route("/categorias")
def categorias():
    return render_template("admin/categorias.html", categorias=GestorCategorias(g.db).listar())


@admin_bp.route("/categorias/nova", methods=["POST"])
def criar_categoria():
    try:
        GestorCategorias(g.db).adicionar(Categoria(nome=request.form.get("nome", "").strip()))
        flash("Categoria criada.", "success")
    except DadosInvalidosError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("admin.categorias"))


@admin_bp.route("/categorias/<int:categoria_id>/remover", methods=["POST"])
def remover_categoria(categoria_id):
    try:
        GestorCategorias(g.db).remover(categoria_id)
        flash("Categoria removida.", "info")
    except NextPointError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("admin.categorias"))