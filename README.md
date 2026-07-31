# API de Gestão de Estoque

API REST para controle de estoque com autenticação JWT, construída com FastAPI, SQLAlchemy e MySQL.

## Funcionalidades

- Cadastro e login de usuários (JWT — access token + refresh token)
- Permissões: primeiro usuário cadastrado vira admin automaticamente; só admins criam/editam/excluem categorias, fornecedores e produtos; qualquer usuário autenticado pode registrar movimentações e consultar relatórios
- CRUD de categorias, fornecedores e produtos, com validação de integridade referencial (não deixa criar produto com categoria/fornecedor inexistente)
- Registro de movimentações de estoque (entrada/saída) com validação de saldo
- Relatórios: resumo de estoque (valor total, produtos com estoque baixo) e produtos mais movimentados
- Paginação em todas as listagens (`skip`/`limit`)
- Tratamento global de exceções (nenhuma rota vaza traceback bruto) e logging estruturado de requisições
- CI com GitHub Actions rodando a suíte de testes a cada push
- Documentação automática via Swagger (`/docs`) e Redoc (`/redoc`)

## Como rodar (Docker — recomendado)

```bash
docker compose up --build
```

A API sobe em `http://localhost:8000`. O MySQL sobe junto, já com o banco `estoque_db` criado.

Depois, crie as tabelas rodando a migração (em outro terminal, com os containers no ar):

```bash
docker compose exec api alembic upgrade head
```

Acesse a documentação interativa em `http://localhost:8000/docs`.

## Como rodar localmente (sem Docker)

1. Suba um MySQL local e crie o banco `estoque_db`.
2. Copie `.env.example` para `.env` e ajuste `DATABASE_URL`.
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Rode as migrações:
   ```bash
   alembic upgrade head
   ```
5. Suba a API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Rodando os testes

O projeto tem uma suíte de testes automatizados com `pytest`, cobrindo autenticação, categorias, fornecedores, produtos e a regra de negócio de movimentações (incluindo o caso de saída maior que o estoque disponível). Os testes rodam contra um banco SQLite em memória — não tocam no seu MySQL.

```bash
pip install -r requirements.txt
pytest -v
```

## Melhorias de engenharia aplicadas

- **Precisão monetária:** `preco` usa `Numeric(10, 2)` em vez de `Float`, evitando erros de arredondamento típicos de ponto flutuante em valores financeiros.
- **Paginação:** todas as rotas de listagem (`/produtos`, `/categorias`, `/fornecedores`, `/movimentacoes`) aceitam `skip` e `limit` e retornam um envelope `{ total, skip, limit, itens }`.
- **Validação de integridade referencial:** criar ou atualizar um produto valida que `categoria_id`/`fornecedor_id` realmente existem antes de gravar, retornando 404 claro em vez de deixar o erro estourar no banco.
- **Rollback em falhas de transação:** toda operação de escrita reverte a sessão do banco (`db.rollback()`) se o commit falhar, evitando que a sessão fique num estado inconsistente para a próxima requisição.

## Gerando uma nova migração


Sempre que alterar `app/models.py`:

```bash
alembic revision --autogenerate -m "descricao da mudanca"
alembic upgrade head
```

## Fluxo de uso básico

1. `POST /auth/registrar` — cria um usuário (o **primeiro** usuário cadastrado vira admin automaticamente)
2. `POST /auth/login` — retorna `access_token` e `refresh_token`
3. Use o `access_token` no header `Authorization: Bearer <token>` nas demais rotas
4. Quando o `access_token` expirar, troque por um novo par de tokens em `POST /auth/refresh`, enviando o `refresh_token` — sem precisar logar de novo
5. Cadastre categorias e fornecedores (requer admin)
6. Cadastre produtos vinculados a eles (requer admin)
7. Registre movimentações (`ENTRADA`/`SAIDA`) em `/movimentacoes` — qualquer usuário autenticado pode
8. Consulte `/relatorios/resumo-estoque` e `/relatorios/mais-movimentados`

## Estrutura do projeto

```
app/
  main.py          -> ponto de entrada, registra os routers
  database.py      -> engine e sessão do SQLAlchemy
  models.py        -> tabelas (usuarios, categorias, fornecedores, produtos, movimentacoes)
  schemas.py        -> validação de entrada/saída (Pydantic)
  security.py       -> hash de senha e geração/validação de JWT
  dependencies.py   -> dependências de autenticação (usuário atual, admin)
  routers/          -> um arquivo por recurso (auth, produtos, categorias, ...)
alembic/             -> migrações de banco de dados
```
