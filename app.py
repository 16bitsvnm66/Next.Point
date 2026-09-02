"""
app.py
--------
Ponto de entrada da aplicação Flask. Cria a app, gere a ligação à base
de dados por pedido (flask.g) e regista os blueprints da loja e da
área de administração.

Correr com:  python3 app.py
"""

from flask import Flask, g, render_template

from database import criar_ligacao_e_iniciar, get_connection
from gestor import GestorCategorias, GestorProdutos
from models import Categoria, EntidadeNaoEncontradaError, Produto

CATEGORIAS_EXEMPLO = ["Roupa", "Calçado", "Acessórios"]

PRODUTOS_EXEMPLO = [
    dict(nome="T-shirt Next Point", categoria="Roupa", tamanho="M", cor="Preto",
         preco=22.50, stock=18, descricao="T-shirt técnica respirável, ideal para jogo."),
    dict(nome="Polo técnico", categoria="Roupa", tamanho="L", cor="Branco",
         preco=34.90, stock=12, descricao="Polo em tecido dry-fit com proteção UV."),
    dict(nome="Calções de jogo", categoria="Roupa", tamanho="M", cor="Azul marinho",
         preco=27.90, stock=9, descricao="Calções leves com bolsos para bolas de padel."),
    dict(nome="Sapatilhas Padel Pro", categoria="Calçado", tamanho="42", cor="Preto/Verde",
         preco=89.90, stock=6, descricao="Sapatilhas com sola aderente para terra batida."),
    dict(nome="Boné Next Point", categoria="Acessórios", tamanho="Único", cor="Preto",
         preco=14.90, stock=2, descricao="Boné ajustável com o logótipo Next Point."),
    dict(nome="Grip para raquete", categoria="Acessórios", tamanho="Único", cor="Branco",
         preco=6.50, stock=25, descricao="Grip anti-derrapante, fácil de aplicar."),
]

def criar_app(db_path=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "next-point-chave-de-desenvolvimento"
    app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
    app.config["DATABASE"] = str(db_path) if db_path else None

    @app.before_request
    def antes_do_pedido():
        g.db = get_connection(app.config["DATABASE"]) if app.config["DATABASE"] else get_connection()

    @app.teardown_appcontext
    def fechar_ligacao(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()        

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

def popular_dados_exemplo_se_vazio(conn):
    gestor_categorias = GestorCategorias(conn)
    gestor_produtos = GestorProdutos(conn)

    if gestor_produtos.listar():
        return  # já há produtos, não faz nada

    mapa_categorias = {}
    for nome in CATEGORIAS_EXEMPLO:
        categoria = gestor_categorias.adicionar(Categoria(nome=nome))
        mapa_categorias[nome] = categoria.id

    for dados_originais in PRODUTOS_EXEMPLO:
        dados = dict(dados_originais)  # cópia: não mutar a lista partilhada
        categoria_id = mapa_categorias[dados.pop("categoria")]
        gestor_produtos.adicionar(Produto(categoria_id=categoria_id, **dados))


app = criar_app()

if __name__ == "__main__":
    conn_inicial = criar_ligacao_e_iniciar()
    popular_dados_exemplo_se_vazio(conn_inicial)
    conn_inicial.close()
    app.run(debug=True)
            