# Surfcasting Região dos Lagos

Plataforma full-stack **Surfcasting Região dos Lagos**, um portal mobile-first para telemetria oceanográfica, conhecimento técnico e gestão editorial de pesca de praia.

O projeto já possui uma base executável em FastAPI com:

- esquema relacional MySQL 8 para usuários, praias, pontos de pesca e posts;
- modelo inicial de recomendações em Neo4j/Cypher;
- integrações HTTP com OpenWeather e Stormglass;
- cálculo explicável do Score de Pesca, de 0 a 100;
- endpoint REST e utilitário de linha de comando;
- testes automatizados do algoritmo e dos tratamentos de JSON;
- ambiente local opcional com Docker Compose.
- persistência MySQL com SQLAlchemy 2;
- cadastro, login OAuth2 e access tokens JWT;
- senhas protegidas com Argon2 e controle RBAC;
- CRUD administrativo de praias e consulta pública somente das publicadas.
- integração contínua no GitHub Actions para validar sintaxe e testes.
- pontos de pesca geográficos com acessibilidade e alertas de risco;
- Academia Long Cast com artigos, tutoriais, vídeos e fichas de equipamentos;
- gestor de mídia com imagens WebP e vídeos H.264 otimizados;
- monitoramento interno de tráfego, latência e consumo das APIs;
- recomendações de espécies consultadas no grafo Neo4j.
- front-end Next.js com SSR, SEO, PWA e operação offline parcial;
- dashboard mobile-first com Score de Pesca explicável e gráficos;
- mapa MapLibre com camadas técnicas, acesso e alertas de risco;
- backoffice integrado por sessão HttpOnly, sem expor o JWT ao navegador;
- CI independente para FastAPI/MySQL e Next.js.
- comunidade com discussões, comentários, reações e moderação;
- gestão de usuários/RBAC e campanhas publicitárias com período controlado.

## Arquitetura inicial

```text
Next.js SSR/PWA
    | BFF / cookie HttpOnly
    v
FastAPI ----> OpenWeather (atmosfera)
    |  `----> Stormglass (mar, vento e maré)
    |
    +-------> MySQL (dados transacionais e CMS)
    `-------> Neo4j (relações e recomendações)
```

O MySQL é a fonte oficial de usuários, conteúdo e locais. O Neo4j armazena relações derivadas entre praia, condições ambientais, técnica/equipamento e espécies. Dados retornados por APIs externas nunca devem ser gravados diretamente como regra permanente sem validação e histórico de origem.

## Estrutura

A árvore comentada do back-end está em [`docs/backend-structure.md`](docs/backend-structure.md).

A arquitetura e operação do front-end estão em [`docs/frontend-pwa.md`](docs/frontend-pwa.md).

A configuração de autenticação e os exemplos do CRUD estão em [`docs/auth-and-beaches.md`](docs/auth-and-beaches.md).

Os scripts de banco estão em:

- [`database/mysql/001_initial_schema.sql`](database/mysql/001_initial_schema.sql)
- [`database/neo4j/001_fishing_recommendation.cypher`](database/neo4j/001_fishing_recommendation.cypher)

## Executar a plataforma completa

Requisitos: Docker com Compose. Crie a configuração do back-end e gere um segredo JWT local:

```bash
cp backend/.env.example backend/.env
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copie a saída para `JWT_SECRET_KEY` em `backend/.env`. Depois, inicie bancos, API e portal:

```bash
docker compose --profile app up --build
```

- Portal/PWA: `http://localhost:3000`
- OpenAPI: `http://localhost:8000/docs`
- Neo4j Browser: `http://localhost:7474`

Crie o primeiro administrador dentro do contêiner da API:

```bash
docker compose exec backend python scripts/create_admin.py
```

### Executar apenas o back-end

Requisitos: Python 3.11 ou superior.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

No Windows PowerShell, ative o ambiente com:

```powershell
.venv\Scripts\Activate.ps1
```

Depois, abra `http://localhost:8000/docs`.

As variáveis `OPENWEATHER_API_KEY`, `STORMGLASS_API_KEY` e `JWT_SECRET_KEY` precisam ser preenchidas no arquivo `.env`. As chaves não devem ser enviadas ao GitHub.

### Executar apenas o front-end

Requisitos: Node.js 24.

```bash
cd frontend
cp .env.example .env.local
npm ci
npm run dev
```

O portal possui dados demonstrativos identificados para permitir navegação antes do primeiro conteúdo no CMS ou da configuração dos provedores meteorológicos. Operações administrativas e dados ao vivo nunca são simulados como sucesso.

### Autenticação e praias

```http
POST /api/v1/auth/register
POST /api/v1/auth/token
GET  /api/v1/auth/me

GET    /api/v1/beaches
GET    /api/v1/beaches/{slug}
GET    /api/v1/admin/beaches
POST   /api/v1/admin/beaches
PATCH  /api/v1/admin/beaches/{id}
DELETE /api/v1/admin/beaches/{id}

GET    /api/v1/beaches/{slug}/points
GET    /api/v1/beaches/{slug}/recommendations
GET    /api/v1/academy/posts
GET    /api/v1/community/threads
POST   /api/v1/community/threads
POST   /api/v1/community/threads/{id}/comments
POST   /api/v1/community/threads/{id}/reactions
GET    /api/v1/ads

GET    /api/v1/admin/posts
POST   /api/v1/admin/posts
POST   /api/v1/admin/media
GET    /api/v1/admin/monitoring
GET    /api/v1/admin/users
GET    /api/v1/admin/community/threads
GET    /api/v1/admin/ads
```

As rotas `/admin` exigem um token de administrador. O script `backend/scripts/create_admin.py` cria o primeiro usuário administrativo sem expor a senha no terminal. A exclusão administrativa arquiva e despublica a praia; pontos de pesca vinculados são preservados.

### Endpoint do Score

```http
GET /api/v1/fishing-score?latitude=-22.93&longitude=-42.49&sea_bearing_deg=160
```

`sea_bearing_deg` representa a direção, em graus, da areia para o mar naquele trecho da praia. Esse dado permite distinguir vento terral de vento maral de forma específica para cada praia.

Também é possível executar o núcleo sem subir a API:

```bash
python scripts/fishing_score_cli.py \
  --latitude -22.93 \
  --longitude -42.49 \
  --sea-bearing 160
```

## Como o Score de Pesca funciona

O score inicial é uma heurística explicável, não uma promessa de captura. A soma máxima é 100 pontos:

| Componente | Peso máximo | Leitura inicial |
|---|---:|---|
| Vento | 30 | Favorece vento terral moderado |
| Maré | 25 | Favorece maré enchendo |
| Ondas | 20 | Considera altura e período do swell |
| Temperatura da água | 10 | Usa uma faixa geral ajustável por espécie |
| Pressão | 10 | Favorece estabilidade atmosférica moderada |
| Lua | 5 | Usa fase calculada localmente |

Os pesos ficam isolados em `backend/app/domain/score.py`, permitindo calibração futura com capturas reais, praia, estação do ano e espécie-alvo. A resposta inclui a pontuação de cada componente, qualidade dos dados e avisos. Quando maré ou swell essenciais estão ausentes, o score fica suspenso (`null`) para não apresentar uma recomendação enganosa.

## APIs utilizadas

- [Stormglass Weather API](https://docs.stormglass.io/)
- [Stormglass Tide API](https://stormglass.io/our-tide-api-better-than-ever/)
- [OpenWeather Current Weather Data](https://openweathermap.org/current)

## Testes

```bash
cd backend
pytest
```

Os testes não consomem as APIs externas e não exigem chaves.

Na CI, um MySQL 8.4 temporário também valida o schema e o round-trip geoespacial de latitude/longitude.

O front-end é validado separadamente:

```bash
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
```

## Mídia

Uploads administrativos aceitam JPG, PNG, WebP, MP4, MOV e WebM. Imagens são redimensionadas e convertidas para WebP; vídeos são transcodificados para MP4/H.264 com `faststart`. O Dockerfile instala FFmpeg e o Compose persiste os arquivos em `./uploads`.

## Ambiente com bancos locais

O Docker Compose sobe MySQL e Neo4j para desenvolvimento:

```bash
docker compose up -d mysql neo4j
```

Credenciais de exemplo existem apenas para desenvolvimento local e podem ser substituídas por variáveis de ambiente. Em produção, use um gerenciador de segredos e conexões TLS.

Para uma base criada por uma versão anterior, aplique em ordem os scripts de `database/migrations/mysql/`. Instalações novas recebem o schema consolidado em `database/mysql/001_initial_schema.sql`.
