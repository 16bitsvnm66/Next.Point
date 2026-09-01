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

    
    from blueprints.loja import loja_bp
    from blueprints.admin import admin_bp
    app.register_blueprint(loja_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.errorhandler(404)
    def pagina_nao_encontrada(_erro):
        return render_template("erro.html", titulo="Página não encontrada",
                                mensagem="A página que procuras não existe."), 404

    @app.errorhandler(EntidadeNaoEncontradaError)
    def entidade_nao_encontrada(erro):
        return render_template("erro.html", titulo="Não encontrado", mensagem=str(erro)), 404

    return app

