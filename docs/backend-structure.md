# Estrutura de pastas do back-end

```text
backend/
├── app/
│   ├── api/
│   │   ├── dependencies/
│   │   │   └── auth.py               # Usuário atual e autorização RBAC
│   │   └── v1/
│   │       ├── routes/
│   │       │   ├── auth.py           # Cadastro, login e perfil
│   │       │   ├── beaches.py        # Consulta pública de praias
│   │       │   ├── admin_beaches.py  # CRUD administrativo de praias
│   │       │   └── score.py          # Endpoint REST do Score de Pesca
│   │       └── router.py             # Agregador das rotas da versão 1
│   ├── core/
│   │   ├── config.py                 # Variáveis de ambiente e configurações
│   │   ├── exceptions.py             # Exceções compartilhadas
│   │   └── security.py               # Argon2 e tokens JWT
│   ├── db/
│   │   ├── base.py                   # Base declarativa SQLAlchemy
│   │   └── session.py                # Engine e ciclo de sessão MySQL
│   ├── domain/
│   │   └── score.py                  # Regra de negócio pura e testável
│   ├── integrations/
│   │   ├── http.py                   # HTTP, timeout e tentativas controladas
│   │   ├── openweather.py            # Adaptador atmosférico
│   │   └── stormglass.py             # Adaptador marítimo e de marés
│   ├── schemas/
│   │   ├── auth.py                   # Contratos de autenticação
│   │   ├── beach.py                  # Contratos de praias
│   │   └── score.py                  # Contratos do score
│   ├── models/                       # Entidades SQLAlchemy
│   ├── repositories/                 # Consultas e persistência MySQL
│   ├── services/
│   │   ├── auth.py                   # Cadastro e autenticação
│   │   ├── beach.py                  # Regras do CRUD de praias
│   │   └── fishing_score.py          # Orquestra provedores e domínio
│   ├── utils/
│   │   └── slug.py                   # Slugs estáveis para SEO
│   └── main.py                       # Inicialização do FastAPI
├── scripts/
│   ├── create_admin.py               # Bootstrap seguro do administrador
│   └── fishing_score_cli.py          # Execução do núcleo via terminal
├── tests/
│   ├── test_integrations.py          # Tratamento dos JSONs externos
│   └── test_score.py                 # Testes da regra de negócio
├── .env.example                      # Modelo sem segredos
├── Dockerfile
├── pyproject.toml
└── requirements.txt
```

## Pastas previstas para as próximas entregas

Quando os CRUDs forem implementados, a camada `app` receberá:

```text
app/
├── media/                            # Compressão e armazenamento de mídia
├── monitoring/                       # Métricas, logs e consumo das APIs
└── workers/                          # Tarefas assíncronas e atualização de telemetria
```

Essa separação mantém o domínio independente de FastAPI, MySQL, Neo4j e fornecedores externos. Assim, uma mudança de API meteorológica não exige reescrever o algoritmo nem o endpoint.
