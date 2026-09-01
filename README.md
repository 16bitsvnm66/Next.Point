# Next Point — Loja Virtual de Artigos de Padel (Flask)

Aplicação web que implementa a proposta de projeto entregue: um catálogo
público onde os clientes veem produtos e fazem encomendas online, e uma
área de administração onde o lojista gere produtos, categorias, clientes
e o estado das encomendas — substituindo o processo manual no WhatsApp.

## Como correr

```bash
pip install -r requirements.txt
python3 app.py
```

Abre depois `http://127.0.0.1:5000` no browser. Na primeira execução é
criada a base de dados `next_point.db` (SQLite), já com produtos de
exemplo.

Área de administração: `http://127.0.0.1:5000/admin/` (ainda sem
autenticação — ver "Limitações" abaixo).

## Como correr os testes

```bash
python3 -m unittest discover -s tests -v
```

## Estrutura do projecto

| Ficheiro / pasta       | Responsabilidade |
|--------------------------|--------------------|
| `database.py`           | Ligação SQLite e criação do esquema (tabelas) |
| `models.py`               | Classes de dados e exceções de negócio |
| `gestor.py`                 | Lógica de negócio: CRUD, regras de stock, cálculo de totais, relatórios |
| `blueprints/loja.py`         | Rotas do cliente: catálogo, ficha de produto, carrinho, checkout |
| `blueprints/admin.py`          | Rotas de administração: produtos, categorias, clientes, encomendas, relatórios |
| `templates/`                     | Páginas HTML (Jinja2 + Bootstrap 5) |
| `static/css/style.css`             | Estilo personalizado (cor de marca Next Point) |
| `static/uploads/`                    | Fotos de produtos enviadas pela área de administração |
| `tests/`                             | Testes automáticos (unitários + rotas) |

## Esquema da base de dados

`categorias`, `produtos` (com `categoria_id`, `imagem_url`),
`clientes`, `encomendas` e `itens_encomenda`.

## Funcionalidades implementadas

- **Catálogo**: listagem com filtros por categoria, tamanho e pesquisa por nome.
- **Ficha de produto** com foto e stock disponível.
- **Carrinho de compras** (guardado na sessão do browser).
- **Checkout**: cria/reaproveita o cliente pelo email, valida stock, cria a encomenda e atualiza o stock automaticamente.
- **Administração**: CRUD de produtos (com upload de foto) e categorias, listagem de clientes, gestão de encomendas (atualizar estado, cancelar com reposição de stock), relatórios (receita total, mais vendidos, stock baixo) e exportação de encomendas em CSV.
- **Upload de imagens**: fotos de produtos carregadas a partir do computador (jpg/png/webp/gif, até 5MB), guardadas em `static/uploads/`.

## Limitações conhecidas (funcionalidades futuras)

- Sem autenticação na área `/admin`.
- Sem pagamento online.
- Sem envio de emails/notificações automáticas.
- Aplicação ainda não publicada em produção (deployment por fazer).
