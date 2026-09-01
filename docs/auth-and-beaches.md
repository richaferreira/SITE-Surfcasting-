# Autenticação, RBAC e CRUD de praias

Esta entrega adiciona a fundação de acesso ao backoffice sem alterar o módulo oceanográfico.

## Segurança adotada

- senhas armazenadas somente como hash Argon2;
- access tokens JWT assinados com HS256;
- validação de expiração, emissor, audiência e tipo do token;
- chave JWT carregada exclusivamente por variável de ambiente;
- endpoints administrativos protegidos pela role `ADMIN`;
- erros de autenticação não revelam se o login ou a senha estava incorreto;
- sessão SQLAlchemy fechada ao final de cada requisição.

O access token dura 30 minutos por padrão. Refresh token, recuperação de senha e verificação de e-mail serão incluídos junto ao front-end de autenticação.

## Preparação

Copie o arquivo de configuração e troque todas as chaves de exemplo:

```bash
cp backend/.env.example backend/.env
```

Para gerar uma chave JWT segura:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Suba os bancos. Na primeira inicialização do volume MySQL, o script `database/mysql/001_initial_schema.sql` cria as tabelas e as roles.

```bash
docker compose up -d mysql neo4j
```

## Criar o primeiro administrador

Com o ambiente Python ativo dentro da pasta `backend`:

```bash
python scripts/create_admin.py \
  --name "Administrador" \
  --username admin \
  --email admin@exemplo.com
```

A senha é solicitada de forma oculta e não fica gravada no histórico do terminal.

## Endpoints

| Método | Endpoint | Acesso | Finalidade |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | Público | Cadastro como usuário comum |
| `POST` | `/api/v1/auth/token` | Público | Login por usuário ou e-mail |
| `GET` | `/api/v1/auth/me` | Autenticado | Perfil da sessão atual |
| `GET` | `/api/v1/beaches` | Público | Lista praias publicadas |
| `GET` | `/api/v1/beaches/{slug}` | Público | Exibe uma praia publicada |
| `GET` | `/api/v1/admin/beaches` | Admin | Lista inclusive rascunhos |
| `POST` | `/api/v1/admin/beaches` | Admin | Cadastra uma praia |
| `PATCH` | `/api/v1/admin/beaches/{id}` | Admin | Atualiza uma praia |
| `DELETE` | `/api/v1/admin/beaches/{id}` | Admin | Arquiva e despublica uma praia |

## Login

O endpoint segue OAuth2 Password Form. O campo `username` aceita tanto nome de usuário quanto e-mail.

```bash
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=SUA_SENHA"
```

Use o token retornado nas rotas administrativas:

```bash
curl http://localhost:8000/api/v1/admin/beaches \
  -H "Authorization: Bearer SEU_ACCESS_TOKEN"
```

## Orientação da praia

O campo `sea_bearing_deg` é obrigatório porque permite ao Score de Pesca calcular se o vento é terral para aquele trecho específico. Ele representa a direção da areia para o mar, entre `0` e menos de `360` graus.

As coordenadas são mantidas em campos numéricos para consumo da API e também atualizam a coluna espacial `POINT SRID 4326` usada pelo mapa e por consultas geográficas do MySQL.

A construção espacial explicita `axis-order=long-lat`, evitando a inversão de eixos do EPSG:4326. A resposta pública omite IDs e datas de auditoria; esses campos permanecem disponíveis somente no backoffice.

Para uma instalação que já executou o schema anterior, aplique uma vez `database/migrations/mysql/002_harden_auth_beaches.sql`. Novos volumes usam diretamente o schema inicial atualizado.
