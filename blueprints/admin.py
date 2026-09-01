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

# ---------------------------------------------------------------- Clientes --
@admin_bp.route("/clientes")
def clientes():
    termo = request.args.get("q", "")
    return render_template("admin/clientes.html", clientes=GestorClientes(g.db).listar(termo_pesquisa=termo),
                            termo=termo)
    
# ------------------------------------------------------------- Encomendas --
@admin_bp.route("/encomendas")
def encomendas():
    estado = request.args.get("estado", "")
    gestor_encomendas = GestorEncomendas(g.db)
    lista = gestor_encomendas.listar(estado=estado)
    return render_template("admin/encomendas.html", encomendas=lista, estado=estado,
                            estados=ESTADOS_ENCOMENDA)


@admin_bp.route("/encomendas/<int:encomenda_id>")
def detalhe_encomenda(encomenda_id):
    gestor_encomendas = GestorEncomendas(g.db)
    encomenda = gestor_encomendas.obter(encomenda_id)
    itens = gestor_encomendas.itens_da_encomenda(encomenda_id)
    return render_template("admin/encomenda_detalhe.html", encomenda=encomenda, itens=itens,
                            estados=ESTADOS_ENCOMENDA)


@admin_bp.route("/encomendas/<int:encomenda_id>/estado", methods=["POST"])
def actualizar_estado_encomenda(encomenda_id):
    novo_estado = request.form.get("estado", "pendente")
    GestorEncomendas(g.db).actualizar_estado(encomenda_id, novo_estado)
    flash("Estado da encomenda atualizado.", "success")
    return redirect(url_for("admin.detalhe_encomenda", encomenda_id=encomenda_id))


@admin_bp.route("/encomendas/<int:encomenda_id>/cancelar", methods=["POST"])
def cancelar_encomenda(encomenda_id):
    try:
        GestorEncomendas(g.db).cancelar(encomenda_id)
        flash("Encomenda cancelada e stock reposto.", "info")
    except NextPointError as erro:
        flash(str(erro), "danger")
    return redirect(url_for("admin.encomendas"))

# ------------------------------------------------------------- Relatórios --
@admin_bp.route("/relatorios")
def relatorios():
    gestor_encomendas = GestorEncomendas(g.db)
    gestor_produtos = GestorProdutos(g.db)
    return render_template(
        "admin/relatorios.html",
        receita_total=gestor_encomendas.relatorio_receita_total(),
        mais_vendidos=gestor_encomendas.relatorio_produtos_mais_vendidos(limite=10),
        stock_baixo=gestor_produtos.produtos_stock_baixo(),
    )


@admin_bp.route("/relatorios/exportar")
def exportar_encomendas_csv():
    encomendas_lista = GestorEncomendas(g.db).listar()
    buffer = io.StringIO()
    escritor = csv.DictWriter(buffer, fieldnames=["id", "data_criacao", "cliente_nome", "estado", "total"])
    escritor.writeheader()
    for encomenda in encomendas_lista:
        escritor.writerow({chave: encomenda[chave] for chave in
                            ["id", "data_criacao", "cliente_nome", "estado", "total"]})
    return Response(
        buffer.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=encomendas_next_point.csv"},
    )