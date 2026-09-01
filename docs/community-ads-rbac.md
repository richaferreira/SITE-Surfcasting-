# Comunidade, anúncios e governança

## Comunidade

Usuários autenticados podem criar discussões, comentar e reagir. O conteúdo é texto puro/Markdown sem HTML arbitrário no navegador. As ações passam por limite de frequência por cliente. Discussões possuem categoria, praia opcional, mídia validada e status `PUBLICADO`, `OCULTO` ou `ARQUIVADO`.

O autor pode arquivar a própria discussão. Administradores podem moderar discussões e comentários. O back-end permanece como autoridade; esconder opções na interface serve apenas para melhorar a experiência.

## RBAC

| Papel | Capacidades principais |
|---|---|
| `USER` | Comunidade e consulta pública |
| `AUTHOR` | Comunidade, conteúdo próprio e mídia |
| `ADMIN` | Todos os módulos, publicação, moderação e usuários |

O serviço de usuários impede desativar ou remover o papel do último administrador ativo.

## Campanhas

Campanhas definem posição, título, imagem, destino, texto alternativo, início, término e estado. A API pública retorna apenas campanhas ativas dentro da janela UTC. Destinos externos exigem HTTPS; imagens aceitam HTTPS ou ativos processados no Gestor de Mídia.

O portal identifica visualmente publicidade e adiciona atributos de link apropriados. Métricas de impressão/clique e faturamento não fazem parte desta fundação e devem ser implementados com consentimento, política de privacidade e retenção mínima de dados.
