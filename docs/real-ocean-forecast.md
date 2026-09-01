# Previsão oceanográfica horária

A camada de telemetria do portal oferece uma série horária real para ondas, vento e condições marítimas através do Stormglass. O dashboard não fabrica curvas quando o provedor não retorna dados suficientes.

## Endpoint público

```http
GET /api/v1/forecast?latitude=-22.97&longitude=-42.03&hours=24
```

Parâmetros:

- `latitude`: entre -90 e 90;
- `longitude`: entre -180 e 180;
- `hours`: entre 6 e 48, com padrão de 24 horas.

A resposta contém:

- `hours`: série horária ordenada com altura e período das ondas, temperatura da água, vento e pressão quando disponíveis;
- `tides`: próximos extremos de maré retornados pelo Stormglass, incluindo tipo (`high` ou `low`) e altura quando disponível;
- `warnings`: degradações parciais, por exemplo quando a previsão marítima funciona mas o serviço de maré falha;
- `data_quality`: cobertura da janela solicitada e quantidade de horas consideradas completas.

## Regras de confiabilidade

A série horária é tratada como dado externo e não é substituída por valores inventados no servidor ou no navegador. Se a previsão horária falhar, o endpoint responde `503`. Se apenas os extremos de maré falharem, a previsão marítima continua disponível e a falha de maré aparece em `warnings`.

O dashboard solicita o Score de Pesca e a previsão em paralelo. O Score continua podendo ser exibido se a série horária estiver temporariamente indisponível. O gráfico só é desenhado quando existem ao menos dois pontos reais com altura de onda e velocidade do vento.

## Rate limiting

`/api/v1/forecast` compartilha a mesma quota pública de `/api/v1/fishing-score`. Isso evita que a inclusão da série horária dobre a capacidade de consultas externas por cliente.

## BFF do Next.js

O front-end acessa a rota por:

```http
GET /api/public/forecast
```

A raiz `forecast` foi adicionada à allowlist explícita do BFF. O proxy continua rejeitando raízes não autorizadas e não funciona como proxy genérico para a API interna.

## Testes

Os testes automatizados cobrem:

- parsing e ordenação da série horária;
- preferência pela fonte `sg` do Stormglass;
- parsing de preamar e baixa-mar com altura;
- preservação da previsão marítima quando apenas a API de maré falha;
- registro da rota `/api/v1/forecast` no FastAPI.

Nenhum teste automatizado consome a API externa real.
