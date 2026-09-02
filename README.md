# Surfcasting Região dos Lagos

Plataforma web mobile-first para pescadores de praia da Região dos Lagos, reunindo telemetria oceanográfica, Score de Pesca explicável, previsão horária, mapa de spots, recomendações em grafo, conteúdo técnico, comunidade e backoffice completo.

## Stack

- **Frontend:** Next.js 16 (Active LTS), React 19, TypeScript e Leaflet/OpenStreetMap.
- **Backend:** Python 3.12 e FastAPI.
- **Relacional:** MySQL 8.4.
- **Grafo:** Neo4j 5 Community.
- **Integrações:** OpenWeather e Stormglass.
- **Infraestrutura local:** Docker Compose.
- **CI:** GitHub Actions com pytest, auditoria npm, typecheck, build e smoke test da stack Docker.

## Arquitetura

```text
Navegador / Mobile
        |
        v
     Next.js :3000
        |
        v
     FastAPI :8000
      /   |    \
     /    |     \
MySQL   Neo4j   APIs externas
:3306   :7687   OpenWeather / Stormglass
```

O MySQL é a fonte transacional oficial. O Neo4j mantém relações explicáveis entre praia, condições ambientais, espécie, técnica e equipamento. As regras do Score ficam no backend; o frontend consome os resultados e nunca contém chaves dos provedores externos.

## Funcionalidades implementadas

### Condições, Score e previsão

- vento, velocidade e direção;
- classificação terral/maral conforme a orientação praia → mar;
- maré enchendo/vazando;
- altura e período das ondas;
- temperatura da água;
- pressão atmosférica;
- fase da lua;
- Score de Pesca de 0 a 100 com breakdown e justificativas;
- previsão marítima horária de 6 a 48 horas;
- Score recalculado para cada horário da previsão.

### Praias, pontos e mapa

- catálogo público de praias;
- página individual com telemetria e previsão;
- mapa Leaflet/OpenStreetMap;
- spots por praia: buraco, coroa, canal de retorno, estrutura e outros;
- acessibilidade, notas de acesso e riscos por spot;
- favoritos por usuário;
- CRUD administrativo completo de praias e pontos;
- publicação/rascunho da praia e ativação/desativação de spots.

### Recomendação Neo4j

O endpoint cruza praia, direção/velocidade do vento, temperatura da água e maré com o grafo. A resposta pode incluir:

```text
Praia
  -> Condição de vento
  -> Condição da água
  -> Espécie
  -> Técnica recomendada
  -> Equipamentos associados
```

O grafo inicial inclui a Praia de Itaúna, Anchova, surf spinning e um conjunto inicial de equipamentos.

### Comunidade

- artigos, tutoriais, vídeos e conteúdo de equipamentos;
- curtidas;
- comentários;
- relatos de captura;
- espécie, praia, isca, técnica, peso e comprimento;
- feed público.

### Autenticação e perfil

- cadastro;
- login por e-mail ou usuário;
- senhas com Argon2;
- access token JWT;
- refresh token JWT rotativo;
- refresh tokens persistidos apenas como hash SHA-256 no MySQL;
- revogação de refresh token no logout;
- renovação automática da sessão no frontend;
- perfis `USER`, `AUTHOR` e `ADMIN`;
- proteção de rotas por função;
- edição de nome, bio e URL do avatar.

### Backoffice

- indicadores gerais;
- gerenciamento de usuários;
- ativar/desativar conta;
- alterar função;
- listar, cadastrar, editar, publicar/despublicar e excluir praias;
- cadastrar, editar, ativar/desativar e excluir spots;
- criar, editar, publicar, arquivar e excluir conteúdo;
- listar, ocultar e restaurar comentários;
- trilha de auditoria das operações administrativas.

## Estrutura principal

```text
.
├── .github/workflows/ci.yml
├── backend/
│   ├── app/
│   │   ├── api/v1/routes/
│   │   ├── core/
│   │   ├── domain/
│   │   ├── integrations/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── db.py
│   │   └── main.py
│   ├── scripts/
│   ├── tests/
│   └── requirements.txt
├── database/
│   ├── mysql/
│   │   ├── 001_initial_schema.sql
│   │   ├── 002_platform_features.sql
│   │   └── 003_auth_sessions.sql
│   └── neo4j/
│       └── 001_fishing_recommendation.cypher
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
└── docker-compose.yml
```

## Subir tudo com Docker

### 1. Criar o arquivo de ambiente

Windows PowerShell:

```powershell
Copy-Item backend\.env.example backend\.env
```

Linux/macOS:

```bash
cp backend/.env.example backend/.env
```

Edite `backend/.env` e altere obrigatoriamente:

```env
JWT_SECRET=gere-uma-chave-longa-e-aleatoria
ACCESS_TOKEN_EXPIRE_MINUTES=720
REFRESH_TOKEN_EXPIRE_DAYS=30
ADMIN_EMAIL=seu-email@exemplo.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=uma-senha-forte
```

Para telemetria real, preencha:

```env
OPENWEATHER_API_KEY=...
STORMGLASS_API_KEY=...
```

Sem essas chaves, o portal continua subindo, porém os recursos que dependem dos provedores externos podem informar indisponibilidade de telemetria/previsão.

### 2. Subir a stack

```bash
docker compose --profile app up -d --build
```

Serviços:

- Web: `http://localhost:3000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Neo4j Browser: `http://localhost:7474`

Ao subir um volume Neo4j novo, o `neo4j-init` aguarda o Bolt, executa `database/neo4j/001_fishing_recommendation.cypher` e termina. O backend só inicia depois desse seed concluir com sucesso.

### 3. Criar o administrador

```bash
docker compose --profile app exec backend python scripts/create_admin.py
```

O container já define `PYTHONPATH=/app`, então os scripts de bootstrap funcionam diretamente dessa forma.

### 4. Inserir a praia inicial no MySQL

```bash
docker compose --profile app exec backend python scripts/seed_initial_data.py
```

Depois disso a Praia de Itaúna aparece no catálogo. O grafo correspondente já foi carregado automaticamente pelo `neo4j-init`.

> Se você já possui volumes antigos e precisa reaplicar todos os scripts de inicialização em desenvolvimento, execute `docker compose --profile app down -v` e depois `docker compose --profile app up -d --build`. **Isso apaga os dados dos volumes locais.**

## Executar sem Docker

Suba MySQL e Neo4j localmente, copie `.env.example` para `.env` e mantenha as URLs com `localhost`. Para o frontend, use Node.js 20.9 ou superior; o CI e o Docker usam Node 22.

Backend:

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app.main:app --reload
```

Frontend, em outro terminal:

```bash
cd frontend
npm install
npm audit --omit=dev --audit-level=high
npm run typecheck
npm run dev
```

## Endpoints principais

```text
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/refresh
POST   /api/v1/auth/logout
GET    /api/v1/auth/me
PATCH  /api/v1/auth/me

GET    /api/v1/beaches
GET    /api/v1/beaches/{slug}
GET    /api/v1/beaches/manage
GET    /api/v1/beaches/{slug}/manage
POST   /api/v1/beaches
PATCH  /api/v1/beaches/{slug}
DELETE /api/v1/beaches/{slug}
POST   /api/v1/beaches/{slug}/points
PATCH  /api/v1/beaches/{slug}/points/{point_id}
DELETE /api/v1/beaches/{slug}/points/{point_id}
POST   /api/v1/beaches/{slug}/favorite
DELETE /api/v1/beaches/{slug}/favorite

GET    /api/v1/fishing-score
GET    /api/v1/forecast
GET    /api/v1/recommendations/{beach_slug}

GET    /api/v1/community/posts
POST   /api/v1/community/posts
GET    /api/v1/community/posts/{post_id}/comments
POST   /api/v1/community/posts/{post_id}/comments
POST   /api/v1/community/posts/{post_id}/like
DELETE /api/v1/community/posts/{post_id}/like
GET    /api/v1/community/catches
POST   /api/v1/community/catches

GET    /api/v1/admin/dashboard
GET    /api/v1/admin/users
PATCH  /api/v1/admin/users/{id}/role
PATCH  /api/v1/admin/users/{id}/active
GET    /api/v1/admin/posts
PATCH  /api/v1/admin/posts/{id}
PATCH  /api/v1/admin/posts/{id}/status
DELETE /api/v1/admin/posts/{id}
GET    /api/v1/admin/comments
DELETE /api/v1/admin/comments/{id}
POST   /api/v1/admin/comments/{id}/restore
```

A documentação completa e testável dos contratos fica disponível no Swagger do FastAPI.

## Testes e CI

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm install
npm audit --omit=dev --audit-level=high
npm run typecheck
npm run build
```

O workflow `.github/workflows/ci.yml` executa essas verificações automaticamente em pull requests e pushes para `main`. O smoke test também sobe MySQL, Neo4j, FastAPI e Next.js, valida o seed do grafo, cria o administrador, insere a praia inicial, testa autenticação/renovação de sessão e consulta endpoints reais.

## Segurança

- Nunca envie `backend/.env` ao GitHub.
- Troque `JWT_SECRET` e a senha administrativa fora de desenvolvimento.
- Refresh tokens são armazenados no banco somente como hash e são rotacionados a cada renovação.
- Use TLS/HTTPS e um gerenciador de segredos em produção.
- As chaves de OpenWeather e Stormglass ficam somente no backend.
- O conteúdo exibido em popups do mapa é inserido como texto, sem HTML não confiável.
- A heurística do Score ajuda no planejamento, mas não substitui avaliação presencial do mar, alertas meteorológicos e regras locais de segurança.
