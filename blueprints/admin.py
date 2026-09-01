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