# 🎾 Next Point

**Loja virtual de artigos de padel** — projeto final da UFCD 5425.

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-lightgrey?logo=sqlite&logoColor=white)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)

---

## 📖 Sobre o projeto

O dono de uma pequena loja de artigos de padel gere atualmente o negócio
através do WhatsApp: os clientes perguntam um a um se um produto está
disponível, em que tamanho e a que preço, sem catálogo organizado nem
controlo estruturado de stock.

O **Next Point** resolve esse problema com uma loja virtual completa:
os clientes consultam o catálogo, montam o carrinho e fazem encomendas
online, sem depender da troca manual de mensagens — e o lojista gere
tudo (produtos, stock, encomendas) numa única área de administração.

## Índice

- [Funcionalidades](#-funcionalidades)
- [Tecnologias](#-tecnologias)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Como instalar e correr](#-como-instalar-e-correr)
- [Rotas principais](#-rotas-principais)
- [Testes](#-testes)
- [Esquema da base de dados](#-esquema-da-base-de-dados)
- [Limitações e trabalho futuro](#-limitações-e-trabalho-futuro)

## ✨ Funcionalidades

**Para o cliente**
- Catálogo com filtros por categoria, tamanho e pesquisa por nome
- Ficha de produto com foto e stock disponível
- Carrinho de compras (sessão do browser)
- Checkout com criação automática da encomenda e validação de stock
- Confirmação e acompanhamento do estado da encomenda

**Para o lojista (área de administração)**
- CRUD de produtos, com upload de foto
- CRUD de categorias
- Listagem de clientes
- Gestão de encomendas: atualizar estado, cancelar com reposição de stock
- Relatórios: receita total, produtos mais vendidos, stock baixo
- Exportação de encomendas em CSV

## 🛠 Tecnologias

| | |
|---|---|
| **Backend** | Python 3, Flask |
| **Base de dados** | SQLite (`sqlite3`, biblioteca padrão) |
| **Frontend** | HTML5, CSS3, Bootstrap 5, Jinja2 |
| **Testes** | `unittest`, Flask test client |

## 📁 Estrutura do projeto

```
next_point_flask/
├── app.py                    # Ponto de entrada da aplicação
├── database.py                # Ligação SQLite e esquema (tabelas)
├── models.py                    # Classes de dados e exceções de negócio
├── gestor.py                      # Lógica de negócio (CRUD, stock, relatórios)
├── requirements.txt
├── blueprints/
│   ├── loja.py                      # Rotas do cliente
│   └── admin.py                      # Rotas de administração
├── templates/                          # Páginas HTML (Jinja2)
│   ├── loja/
│   └── admin/
├── static/
│   ├── css/style.css                     # Estilo (marca Next Point)
│   └── uploads/                            # Fotos de produtos
└── tests/                                    # Testes automáticos
    ├── test_encomendas.py
    ├── test_produtos_categorias.py
    └── test_rotas.py
```

## 🚀 Como instalar e correr

```bash
# 1. Criar o ambiente virtual
python -m venv venv

# 2. Ativar (Windows PowerShell)
.\venv\Scripts\Activate.ps1
# — ou no Linux/Mac —
source venv/bin/activate

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Correr a aplicação
python app.py
```

Abre depois **http://127.0.0.1:5000** no browser (catálogo) e
**http://127.0.0.1:5000/admin/** (área de administração).

Na primeira execução é criada automaticamente a base de dados
`next_point.db`, já com produtos de exemplo.

> ⚠️ A área `/admin` ainda não tem autenticação — ver
> [Limitações](#-limitações-e-trabalho-futuro).

## 🧭 Rotas principais

| Rota | Método | Descrição |
|---|---|---|
| `/` | GET | Catálogo de produtos |
| `/produto/<id>` | GET | Ficha de produto |
| `/carrinho/adicionar/<id>` | POST | Adicionar produto ao carrinho |
| `/carrinho` | GET | Ver carrinho |
| `/checkout` | GET/POST | Finalizar encomenda |
| `/encomenda/<id>` | GET | Confirmação da encomenda |
| `/admin/` | GET | Dashboard da administração |
| `/admin/produtos` | GET | Gestão de produtos |
| `/admin/categorias` | GET | Gestão de categorias |
| `/admin/encomendas` | GET | Gestão de encomendas |
| `/admin/relatorios` | GET | Relatórios e exportação CSV |

## ✅ Testes

```bash
python -m unittest discover -s tests -v
```

Cobrem a lógica de negócio (validações, cálculo de totais, regras de
stock) e o comportamento ponta-a-ponta das rotas, através do Flask test
client — sem precisar de um browser real.

## 🗄 Esquema da base de dados

```
Categoria 1───N Produto 1───N ItemEncomenda N───1 Encomenda N───1 Cliente
```

`categorias` · `produtos` (com `categoria_id`, `imagem_url`) ·
`clientes` · `encomendas` · `itens_encomenda`

## 🔭 Limitações e trabalho futuro

- [ ] Autenticação na área de administração
- [ ] Pagamento online
- [ ] Notificações automáticas por email
- [ ] Deployment em ambiente de produção
- [ ] Dashboard de vendas / relatórios em PDF

---

<p align="center"><sub>Projeto académico — UFCD 5425</sub></p>
