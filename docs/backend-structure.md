# Estrutura de pastas do back-end

O back-end segue separação por responsabilidades. Rotas HTTP ficam na camada de API, regras de negócio em serviços/domínio, persistência em repositórios e integrações externas em adaptadores próprios.

```text
backend/
├── app/
│   ├── api/
│   │   ├── dependencies/
│   │   │   ├── auth.py               # Usuário atual e autorização RBAC
│   │   │   └── rate_limit.py         # Limites de autenticação, score e comunidade
│   │   └── v1/
│   │       ├── routes/
│   │       │   ├── auth.py           # Cadastro, login e perfil
│   │       │   ├── beaches.py        # Consulta pública de praias
│   │       │   ├── fishing_points.py # Pontos técnicos por praia
│   │       │   ├── score.py          # Score de Pesca atual
│   │       │   ├── forecast.py       # Previsão oceanográfica horária
│   │       │   ├── posts.py          # Academia Long Cast pública
│   │       │   ├── community.py      # Discussões, comentários e reações
│   │       │   ├── ads.py            # Campanhas publicitárias ativas
│   │       │   ├── recommendations.py# Recomendações consultadas no Neo4j
│   │       │   └── admin_*.py        # Backoffice protegido por RBAC
│   │       └── router.py             # Agregador das rotas da versão 1
│   ├── core/
│   │   ├── config.py                 # Variáveis de ambiente e configurações
│   │   ├── exceptions.py             # Exceções de aplicação
│   │   ├── rate_limit.py             # Registry de rate limiting em memória
│   │   └── security.py               # Argon2 e tokens JWT
│   ├── db/
│   │   ├── base.py                   # Base declarativa SQLAlchemy
│   │   └── session.py                # Engine e ciclo de sessão MySQL
│   ├── domain/
│   │   └── score.py                  # Regra pura do Score de Pesca
│   ├── integrations/
│   │   ├── http.py                   # HTTP, timeout e tentativas controladas
│   │   ├── openweather.py            # Adaptador atmosférico
│   │   ├── stormglass.py             # Mar, vento, previsão e marés
│   │   └── neo4j_recommendations.py  # Consultas Cypher parametrizadas
│   ├── models/                       # Entidades SQLAlchemy
│   ├── monitoring/
│   │   └── registry.py               # Volume, latência e provedores externos
│   ├── repositories/                 # Consultas e persistência MySQL
│   ├── schemas/                      # Contratos Pydantic da API
│   ├── services/
│   │   ├── auth.py                   # Cadastro e autenticação
│   │   ├── beach.py                  # Regras das praias
│   │   ├── fishing_point.py          # Regras dos pontos técnicos
│   │   ├── fishing_score.py          # Orquestra Score e provedores
│   │   ├── marine_forecast.py        # Orquestra previsão horária e marés
│   │   ├── media.py                  # Validação e processamento de mídia
│   │   ├── post.py                   # Workflow editorial
│   │   ├── community.py              # Regras da comunidade
│   │   ├── ad.py                     # Regras das campanhas
│   │   └── user_admin.py             # Governança administrativa de usuários
│   ├── utils/
│   │   └── slug.py                   # Slugs estáveis para SEO
│   └── main.py                       # Inicialização do FastAPI e /health
├── scripts/
│   ├── create_admin.py               # Bootstrap seguro do administrador
│   └── fishing_score_cli.py          # Execução do núcleo via terminal
├── tests/                            # Domínio, integrações, segurança e MySQL real na CI
├── .env.example                      # Modelo sem segredos
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

## Persistência e integrações

O MySQL é a fonte transacional de usuários, praias, pontos, conteúdo, comunidade, mídia e anúncios. O Neo4j mantém relações usadas pelo motor de recomendação. OpenWeather e Stormglass entram por adaptadores separados e não vazam formatos de fornecedores para o domínio.

A previsão horária do Stormglass é tratada como telemetria externa: o front-end só desenha a tendência quando recebe pontos reais. O Score de Pesca pode continuar disponível mesmo se a série horária estiver temporariamente indisponível.

## Escalabilidade operacional

Cache de score, rate limiting e métricas ainda são registries locais ao processo. Isso é adequado para desenvolvimento e uma única réplica. Em implantação com múltiplas réplicas, a evolução recomendada é externalizar estado efêmero para Redis e observabilidade para OpenTelemetry/um backend de métricas, preservando os contratos HTTP existentes.

Tarefas periódicas não são iniciadas implicitamente dentro do processo web. Caso seja necessário pré-aquecer telemetria ou executar rotinas programadas em produção, a execução deve ocorrer por worker/cron dedicado para evitar duplicação em ambientes com múltiplas réplicas.
