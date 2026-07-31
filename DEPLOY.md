# Deploy público (Railway)

Este guia usa o [Railway](https://railway.app) por ser o caminho mais rápido: ele builda o `Dockerfile` automaticamente e oferece um plugin de MySQL gerenciado, sem precisar configurar servidor.

## Passo a passo

1. Suba o projeto para um repositório no GitHub (se ainda não estiver lá).
2. Crie uma conta em https://railway.app (dá para entrar com GitHub).
3. **New Project → Deploy from GitHub repo** → selecione o repositório do projeto.
4. No mesmo projeto Railway, clique em **+ New → Database → Add MySQL**. Isso sobe um MySQL gerenciado e gera variáveis de conexão automaticamente.
5. No serviço da API (não no banco), vá em **Variables** e adicione:
   - `DATABASE_URL` → monte usando as variáveis que o Railway gerou para o MySQL, no formato:
     ```
     mysql+pymysql://${{MYSQL_USER}}:${{MYSQL_PASSWORD}}@${{MYSQL_HOST}}:${{MYSQL_PORT}}/${{MYSQL_DATABASE}}
     ```
     (o Railway permite referenciar variáveis de outro serviço com essa sintaxe `${{...}}`)
   - `SECRET_KEY` → gere uma chave forte, por exemplo rodando localmente: `python -c "import secrets; print(secrets.token_hex(32))"`
   - `ACCESS_TOKEN_EXPIRE_MINUTES` → `60`
   - `REFRESH_TOKEN_EXPIRE_DAYS` → `7`
6. Railway detecta o `Dockerfile` e builda automaticamente. Se preferir não usar Docker, ele também detecta o `Procfile` incluso no projeto.
7. Depois do primeiro deploy, rode as migrações. No painel do Railway, abra o terminal do serviço (**Settings → aba Deploy → "Shell"**, ou via [Railway CLI](https://docs.railway.app/guides/cli) `railway run alembic upgrade head`).
8. O Railway gera uma URL pública tipo `https://seu-projeto.up.railway.app` — é esse link que vai no currículo/README, junto de `/docs` para a documentação interativa.

## Alternativas

- **Render** (https://render.com): processo parecido — Web Service a partir do `Dockerfile`, mais um PostgreSQL/MySQL gerenciado à parte (o plano gratuito do Render só oferece PostgreSQL gerenciado; para MySQL, use um serviço externo como o PlanetScale ou Railway só para o banco).
- **Fly.io**: bom para quem já tem familiaridade com CLI; requer `fly.toml` (não incluído aqui, mas o `Dockerfile` já é compatível).

## Checklist antes de divulgar a URL publicamente

- [ ] `SECRET_KEY` trocada para um valor gerado (nunca a chave de desenvolvimento do repositório)
- [ ] `--reload` removido do comando de start em produção (o `Dockerfile` já usa a versão sem reload no deploy)
- [ ] Migrações rodadas (`alembic upgrade head`) contra o banco de produção
- [ ] Testado `/health` retornando 200 antes de compartilhar o link
