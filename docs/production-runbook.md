# Runbook de produção

## Objetivo

Este documento descreve o procedimento operacional mínimo para publicar, atualizar, monitorar, fazer backup e restaurar a plataforma Surfcasting Região dos Lagos.

## Pré-requisitos

- Linux com Docker Engine e Docker Compose atuais;
- domínio apontando para o IP público do servidor;
- portas TCP 80/443 e UDP 443 liberadas;
- SMTP transacional válido;
- chaves OpenWeather e Stormglass;
- armazenamento persistente e rotina externa para copiar os backups para outro local.

## 1. Configurar o ambiente

```bash
cp deploy/.env.production.example deploy/.env.production
```

Preencha todos os valores marcados como obrigatórios. Gere senhas e segredo JWT longos e aleatórios. Nunca envie `deploy/.env.production` ao GitHub.

A aplicação valida a configuração quando `APP_ENV=production` e interrompe o boot se detectar segredo JWT fraco/padrão, senha administrativa fraca/padrão, wildcard CORS, cookie sem `Secure`, frontend sem HTTPS, Neo4j sem senha ou SMTP ausente.

## 2. DNS e HTTPS

Defina `SITE_DOMAIN` com o domínio público. O Caddy recebe tráfego em 80/443, solicita e renova certificados automaticamente e encaminha:

- `/api/*`, `/health*`, `/media/*`, `/docs*` e `/openapi.json` para FastAPI;
- demais caminhos para Next.js.

MySQL, Neo4j, FastAPI e Next.js ficam apenas na rede privada do Compose em produção.

## 3. Primeira inicialização

```bash
docker compose --env-file deploy/.env.production -f docker-compose.production.yml config --quiet
docker compose --env-file deploy/.env.production -f docker-compose.production.yml up -d --build
```

Acompanhe:

```bash
docker compose --env-file deploy/.env.production -f docker-compose.production.yml ps
docker compose --env-file deploy/.env.production -f docker-compose.production.yml logs -f --tail=200
```

Crie/atualize o administrador e o catálogo regional:

```bash
docker compose --env-file deploy/.env.production -f docker-compose.production.yml exec -T backend python scripts/create_admin.py
docker compose --env-file deploy/.env.production -f docker-compose.production.yml exec -T backend python scripts/seed_initial_data.py
docker compose --env-file deploy/.env.production -f docker-compose.production.yml exec -T backend python scripts/verify_graph.py
```

Valide externamente:

```bash
curl --fail https://SEU_DOMINIO/health/live
curl --fail https://SEU_DOMINIO/health/ready
```

## 4. Atualização segura

Antes de atualizar:

```bash
COMPOSE_FILE=docker-compose.production.yml BACKUP_DIR=backups ./ops/backup.sh
```

Depois:

```bash
git pull --ff-only
docker compose --env-file deploy/.env.production -f docker-compose.production.yml build --pull
docker compose --env-file deploy/.env.production -f docker-compose.production.yml up -d
docker compose --env-file deploy/.env.production -f docker-compose.production.yml exec -T backend python scripts/verify_graph.py
curl --fail https://SEU_DOMINIO/health/ready
```

## 5. Backup

`ops/backup.sh` produz um diretório versionado com:

- dump MySQL compactado;
- dump Neo4j consistente;
- mídia enviada pelos usuários;
- manifesto;
- checksums SHA-256.

Execute ao menos diariamente e copie o diretório resultante para armazenamento fora do servidor. Uma política prática é 7 diários, 4 semanais e 12 mensais, ajustada ao volume real.

## 6. Restore

Teste restauração periodicamente em ambiente isolado. Nunca considere backup válido apenas porque o arquivo existe.

```bash
COMPOSE_FILE=docker-compose.production.yml ./ops/restore.sh backups/AAAAMMDDTHHMMSSZ
```

O script valida checksums, restaura MySQL, Neo4j e mídia, reinicia a aplicação e exige readiness verde.

## 7. Observabilidade

- `GET /health/live`: processo FastAPI vivo;
- `GET /health/ready`: MySQL e Neo4j acessíveis;
- `GET /api/v1/admin/monitoring`: métricas administrativas de tráfego, latência, erros e provedores externos;
- logs de requisição incluem `request_id`;
- Caddy registra acesso em JSON.

Defina monitor externo para `/health/ready` e alerte quando houver indisponibilidade ou aumento persistente de latência/5xx.

## 8. Testes antes do release

```bash
cd backend
pytest

cd ../frontend
npm install
npm audit --omit=dev --audit-level=high
npm run typecheck
npm run build
npm run test:e2e

cd ..
python ops/load_test.py --base-url http://localhost:8000 --requests 200 --concurrency 20
```

O GitHub Actions executa backend, frontend, stack real, MySQL, Neo4j, autenticação HttpOnly/CSRF, PWA/SEO, smoke de carga e Playwright.

## 9. Incidente de segurança

Em suspeita de comprometimento:

1. retire o serviço da exposição pública se necessário;
2. preserve logs;
3. troque `JWT_SECRET`, senhas de banco, SMTP e chaves externas;
4. revogue sessões persistidas em `refresh_tokens`;
5. restaure backup apenas se houver evidência de alteração de dados;
6. valide `/health/ready`, autenticação e operações administrativas antes de reabrir;
7. documente causa, janela do incidente e ações preventivas.

## 10. O que depende do operador

O repositório fornece a configuração de produção, mas não pode decidir ou adquirir domínio, servidor, conta SMTP ou chaves pagas. Esses valores são externos ao código e devem ser provisionados pelo responsável pela infraestrutura.
