# Surfcasting Região dos Lagos

Portal mobile-first para pesca de praia na Região dos Lagos: telemetria oceanográfica, Score de Pesca explicável, previsão horária, catálogo geográfico, mapa de spots, recomendações Neo4j, comunidade, PWA e backoffice.

## Estado do projeto

A aplicação está estruturada para desenvolvimento e implantação com Docker. O release é validado por CI com backend, frontend, MySQL, Neo4j, autenticação por cookies HttpOnly/CSRF, PWA/SEO, Playwright e smoke de carga.

Para publicação pública ainda é necessário provisionar recursos externos que não pertencem ao código: **domínio/DNS, servidor, conta SMTP e chaves reais OpenWeather/Stormglass**. A configuração de produção desses recursos está pronta em `docker-compose.production.yml` e `deploy/`.

## Stack

- **Frontend:** Next.js 16.3.4, React 19, TypeScript, Leaflet/OpenStreetMap e PWA.
- **Backend:** Python 3.12 + FastAPI.
- **Banco relacional:** MySQL 8.4.
- **Grafo:** Neo4j 5 Community.
- **Integrações:** OpenWeather e Stormglass.
- **Proxy/HTTPS:** Caddy.
- **E2E:** Playwright.
- **CI:** GitHub Actions.

## Segurança de conta

- Argon2 para senhas;
- JWT de acesso curto e refresh rotativo;
- tokens de sessão entregues somente por **cookies HttpOnly**;
- nenhum JWT salvo em `localStorage`;
- cookie CSRF separado + header obrigatório para operações autenticadas mutáveis;
- refresh persistido no MySQL somente como SHA-256;
- revogação no logout e após redefinição de senha;
- rate limiting de autenticação, comunidade e APIs públicas;
- verificação de e-mail;
- recuperação/redefinição de senha;
- validação rígida de configuração quando `APP_ENV=production`;
- headers de segurança e HSTS em produção.

## Produto

### Oceanografia e inteligência

- Score de Pesca de 0 a 100 com justificativas;
- vento, pressão, onda, período, temperatura da água e maré;
- previsão horária de 6 a 48 horas;
- recomendações por praia/vento/temperatura/maré no Neo4j;
- técnica e equipamentos genéricos associados à recomendação.

### Catálogo regional

O seed inicial publica 8 referências geográficas:

1. Praia de Itaúna — Saquarema;
2. Praia da Vila — Saquarema;
3. Praia de Jaconé — Saquarema;
4. Praia de Barra Nova — Saquarema;
5. Praia de Massambaba — Arraial do Cabo;
6. Praia Grande — Arraial do Cabo;
7. Praia do Foguete — Cabo Frio;
8. Praia do Peró — Cabo Frio.

As fontes geográficas e critérios editoriais estão em [`docs/regional-data-sources.md`](docs/regional-data-sources.md). Spots, canais, buracos, estruturas, acessos e riscos específicos **não são fabricados pelo seed** e devem ser validados antes da publicação.

### Comunidade

- artigos/tutorial/conteúdo técnico;
- curtidas e comentários;
- registro de capturas com foto;
- upload validado de JPG/PNG/WebP e normalização WebP;
- denúncias de posts/comentários;
- notificações de interação;
- moderação administrativa;
- analytics próprio sem tracker publicitário externo.

### Backoffice

- dashboard;
- usuários/RBAC;
- praias e spots;
- conteúdo e comentários;
- fila de denúncias;
- métricas de tráfego, latência e erros;
- estado de MySQL/Neo4j e provedores externos;
- trilha de auditoria.

### Web/PWA/SEO

- PWA instalável;
- service worker com cache apenas de conteúdo público seguro;
- API/admin excluídos do cache offline;
- página offline;
- `manifest.webmanifest`;
- sitemap e robots dinâmicos;
- OpenGraph/Twitter metadata.

## Desenvolvimento local

### 1. Ambiente

```bash
cp backend/.env.example backend/.env
```

No PowerShell:

```powershell
Copy-Item backend\.env.example backend\.env
```

Troque `JWT_SECRET` e `ADMIN_PASSWORD`. Para telemetria real, informe `OPENWEATHER_API_KEY` e `STORMGLASS_API_KEY`. SMTP pode permanecer vazio em desenvolvimento; e-mails transacionais são registrados no log em vez de enviados.

### 2. Stack completa

```bash
docker compose --profile app up -d --build
```

- Portal: `http://localhost:3000`
- Swagger: `http://localhost:8000/docs`
- Liveness: `http://localhost:8000/health/live`
- Readiness: `http://localhost:8000/health/ready`
- Neo4j Browser: `http://localhost:7474`

### 3. Bootstrap

```bash
docker compose --profile app exec -T backend python scripts/create_admin.py
docker compose --profile app exec -T backend python scripts/seed_initial_data.py
docker compose --profile app exec -T backend python scripts/verify_graph.py
```

## Testes

Backend:

```bash
cd backend
pip install -r requirements.txt
pytest
```

Frontend:

```bash
cd frontend
npm install
npm audit --omit=dev --audit-level=high
npm run typecheck
npm run build
npx playwright install chromium
npm run test:e2e
```

Smoke de carga, com a stack ativa:

```bash
python ops/load_test.py --base-url http://localhost:8000 --requests 200 --concurrency 20
```

## Produção

O procedimento completo está em [`docs/production-runbook.md`](docs/production-runbook.md).

Resumo:

```bash
cp deploy/.env.production.example deploy/.env.production
# preencher domínio, senhas, SMTP e chaves externas

docker compose --env-file deploy/.env.production -f docker-compose.production.yml config --quiet
docker compose --env-file deploy/.env.production -f docker-compose.production.yml up -d --build
```

O Caddy publica apenas 80/443 e gerencia HTTPS. MySQL, Neo4j, FastAPI e Next.js permanecem na rede privada do Compose.

## Backup e restore

```bash
COMPOSE_FILE=docker-compose.production.yml ./ops/backup.sh
COMPOSE_FILE=docker-compose.production.yml ./ops/restore.sh backups/AAAAMMDDTHHMMSSZ
```

Os backups incluem MySQL, Neo4j, uploads, manifesto e SHA-256. Mantenha cópia fora do host e teste restauração periodicamente.

## Estrutura

```text
.
├── .github/workflows/ci.yml
├── backend/
│   ├── app/
│   ├── scripts/
│   └── tests/
├── database/
│   ├── mysql/
│   └── neo4j/
├── deploy/
│   ├── .env.production.example
│   └── Caddyfile
├── docs/
│   ├── production-runbook.md
│   └── regional-data-sources.md
├── frontend/
│   ├── app/
│   ├── components/
│   ├── e2e/
│   └── public/
├── ops/
│   ├── backup.sh
│   ├── restore.sh
│   └── load_test.py
├── docker-compose.yml
└── docker-compose.production.yml
```

## Nota de responsabilidade

Score, previsão e recomendações são ferramentas de apoio ao planejamento. Não substituem avaliação presencial do mar, avisos oficiais, regras de unidades de conservação, sinalização, licenças ou decisões de segurança.
