# Mapa, Academia Long Cast e Backoffice

## Pontos de pesca

Cada ponto pertence a uma praia e possui coordenadas escalares e `POINT SRID 4326`. O contrato público inclui tipo estrutural, acessibilidade, instruções de acesso, riscos e data da última verificação. A desativação preserva o histórico.

## Academia Long Cast

Conteúdos seguem o fluxo `RASCUNHO -> EM_REVISAO -> PUBLICADO -> ARQUIVADO`.

- `AUTHOR` cria e edita apenas o próprio conteúdo;
- somente `ADMIN` publica;
- listagens públicas retornam resumos leves para o mobile;
- detalhes incluem conteúdo e ficha técnica quando o tipo é `EQUIPAMENTO`;
- título e descrição SEO possuem limites compatíveis com resultados de busca.

As fichas suportam vara de 4,5 m, construção tubular, molinete 9000, linha monofilamento 0,18 mm, shock leader cônico, faixa de peso de arremesso e atributos extras em JSON.

## Gestor de mídia

O servidor não usa o nome enviado como caminho. Cada arquivo recebe identificador aleatório e passa por validação real do decodificador.

- imagens: WebP, dimensão máxima e qualidade configuráveis;
- vídeos: MP4/H.264/AAC, remoção de metadados e `faststart`;
- limite de upload aplicado durante streaming;
- SVG e formatos não previstos são rejeitados;
- arquivos temporários ficam fora da pasta pública.

## Monitoramento e resiliência

O backoffice expõe volume e latência HTTP, distribuição de status e métricas por provedor externo. O score usa cache geográfico limitado e autenticação/score possuem limites por cliente. Para múltiplas réplicas, o próximo passo operacional é substituir os registries em memória por Redis/OpenTelemetry sem alterar os contratos HTTP.

## Migrações

Bancos já existentes devem aplicar, em ordem:

1. `database/migrations/mysql/002_harden_auth_beaches.sql`;
2. `database/migrations/mysql/003_academy_equipment_specs.sql`;
3. `database/migrations/mysql/004_media_assets.sql`.
