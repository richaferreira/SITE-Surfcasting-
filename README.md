# Surfcasting Região dos Lagos

Plataforma web mobile-first para pescadores de praia da Região dos Lagos, reunindo telemetria oceanográfica, Score de Pesca explicável, catálogo de praias e pontos, recomendações em grafo, conteúdo técnico, comunidade e backoffice.

## Stack

- **Frontend:** Next.js 15, React 19 e TypeScript.
- **Backend:** Python 3.11+ e FastAPI.
- **Relacional:** MySQL 8.4.
- **Grafo:** Neo4j 5 Community.
- **Integrações:** OpenWeather e Stormglass.
- **Infraestrutura local:** Docker Compose.
- **CI:** GitHub Actions com pytest, typecheck e build do Next.js.

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

O MySQL é a fonte transacional oficial. O Neo4j mantém relações entre praia, condição ambiental e espécie. As regras do Score permanecem no backend; o frontend apenas consome os resultados.

## Funcionalidades implementadas

### Condições e Score de Pesca

- vento e direção;
- classificação terral/maral conforme orientação da praia;
- maré;
- altura e período das ondas;
- temperatura da água;
- pressão;
- fase da lua;
- Score de Pesca de 0 a 100 com breakdown e justificativas.

### Praias e pontos

- catálogo público de praias;
- página individual com telemetria;
- cadastro administrativo;
- pontos de pesca por praia;
- favoritos por usuário;
- coordenadas geográficas e direção praia → mar.

### Recomendação Neo4j

O endpoint cruza praia, direção/velocidade do vento, temperatura da água e maré com o grafo para sugerir espécies favorecidas. O script inicial inclui a relação de exemplo da Praia de Itaúna com Anchova.

### Comunidade

- artigos e tutoriais;
- curtidas;
- comentários;
- relatos de captura;
- espécie, praia, isca, técnica, peso e comprimento;
- feed público.

### Autenticação e autorização

- cadastro;
- login por e-mail ou usuário;
- senhas com Argon2;
- JWT;
- perfis `USER`, `AUTHOR` e `ADMIN`;
- proteção de rotas por função.

### Backoffice

- indicadores gerais;
- gerenciamento de usuários;
- ativar/desativar conta;
- alterar função;
- cadastrar praia;
- publicar conteúdo;
- alterar status de publicação via API;
- ocultar comentários via API;
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
│   └── neo4j/
├── frontend/
│   ├── app/
│   ├── components/
│   └── lib/
└── docker-compose.yml
```

## Subir tudo com Docker

### 1. Criar o arquivo de ambiente

No Windows PowerShell:

```powershell
Copy-Item backend\.env.example backend\.env
```

No Linux/macOS:

```bash
cp backend/.env.example backend/.env
```

Edite `backend/.env` e altere obrigatoriamente:

```env
JWT_SECRET=gere-uma-chave-longa-e-aleatoria
ADMIN_EMAIL=seu-email@exemplo.com
ADMIN_USERNAME=admin
ADMIN_PASSWORD=uma-senha-forte
```

Para telemetria real, preencha também:

```env
OPENWEATHER_API_KEY=...
STORMGLASS_API_KEY=...
```

### 2. Subir a stack

```bash
docker compose --profile app up -d --build
```

Serviços:

- Web: `http://localhost:3000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Neo4j Browser: `http://localhost:7474`

### 3. Criar o administrador

```bash
docker compose --profile app exec backend python scripts/create_admin.py
```

### 4. Inserir a praia inicial

```bash
docker compose --profile app exec backend python scripts/seed_initial_data.py
```

Depois disso a Praia de Itaúna aparece no catálogo e sua relação inicial de recomendação já existe no Neo4j.

> Se você já possuía um volume MySQL criado antes da inclusão de `002_platform_features.sql`, recrie o ambiente de desenvolvimento uma vez para aplicar todos os scripts: `docker compose down -v` e depois `docker compose --profile app up -d --build`. Isso apaga os dados locais do volume, portanto use apenas em desenvolvimento.

## Executar sem Docker

Suba MySQL e Neo4j localmente, copie o `.env.example` para `.env` e mantenha as URLs com `localhost`.

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
npm run typecheck
npm run dev
```

## Endpoints principais

```text
POST   /api/v1/auth/register
POST   /api/v1/auth/login
GET    /api/v1/auth/me

GET    /api/v1/beaches
GET    /api/v1/beaches/{slug}
POST   /api/v1/beaches
POST   /api/v1/beaches/{slug}/points
POST   /api/v1/beaches/{slug}/favorite

GET    /api/v1/fishing-score
GET    /api/v1/recommendations/{beach_slug}

GET    /api/v1/community/posts
POST   /api/v1/community/posts
POST   /api/v1/community/posts/{id}/comments
POST   /api/v1/community/posts/{id}/like
GET    /api/v1/community/catches
POST   /api/v1/community/catches

GET    /api/v1/admin/dashboard
GET    /api/v1/admin/users
PATCH  /api/v1/admin/users/{id}/role
PATCH  /api/v1/admin/users/{id}/active
PATCH  /api/v1/admin/posts/{id}/status
DELETE /api/v1/admin/comments/{id}
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
npm run typecheck
npm run build
```

O workflow `.github/workflows/ci.yml` executa essas verificações automaticamente em pull requests e pushes para `main`.

## Segurança

- Nunca envie `backend/.env` ao GitHub.
- Troque `JWT_SECRET` e a senha administrativa fora de desenvolvimento.
- Use TLS/HTTPS e um gerenciador de segredos em produção.
- As chaves de OpenWeather e Stormglass ficam somente no backend.
- A heurística do Score ajuda no planejamento, mas não substitui avaliação presencial do mar, alertas meteorológicos e regras locais de segurança.
