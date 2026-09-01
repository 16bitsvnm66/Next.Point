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