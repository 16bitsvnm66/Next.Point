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
            
            