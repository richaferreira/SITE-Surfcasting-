# Estrutura de pastas do back-end

```text
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       │   └── score.py          # Endpoint REST do Score de Pesca
│   │       └── router.py             # Agregador das rotas da versão 1
│   ├── core/
│   │   ├── config.py                 # Variáveis de ambiente e configurações
│   │   └── exceptions.py             # Exceções compartilhadas
│   ├── domain/
│   │   └── score.py                  # Regra de negócio pura e testável
│   ├── integrations/
│   │   ├── http.py                   # HTTP, timeout e tentativas controladas
│   │   ├── openweather.py            # Adaptador atmosférico
│   │   └── stormglass.py             # Adaptador marítimo e de marés
│   ├── schemas/
│   │   └── score.py                  # Contratos de entrada e saída da API
│   ├── services/
│   │   └── fishing_score.py          # Orquestra provedores e domínio
│   └── main.py                       # Inicialização do FastAPI
├── scripts/
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
├── db/                               # Sessões MySQL e Neo4j
├── models/                           # Mapeamentos SQLAlchemy
├── repositories/                     # Acesso persistente sem regra de negócio
├── security/                         # JWT, hashing e RBAC
├── media/                            # Compressão e armazenamento de mídia
├── monitoring/                       # Métricas, logs e consumo das APIs
└── workers/                          # Tarefas assíncronas e atualização de telemetria
```

Essa separação mantém o domínio independente de FastAPI, MySQL, Neo4j e fornecedores externos. Assim, uma mudança de API meteorológica não exige reescrever o algoritmo nem o endpoint.
