# Front-end SSR/PWA

O portal usa Next.js 16 com App Router, React, TypeScript, MapLibre e Recharts. As páginas públicas são renderizadas no servidor e revalidadas, preservando SEO e uma primeira carga leve. Quando a API ainda está vazia ou indisponível, o site exibe dados demonstrativos explicitamente identificados.

## Rotas

| Rota | Função |
|---|---|
| `/` | Dashboard, Score de Pesca, qualidade dos dados e tendência |
| `/mapa` | Praias, camadas técnicas, acesso e risco |
| `/academia` | Biblioteca de artigos, vídeos, tutoriais e equipamentos |
| `/academia/[slug]` | Conteúdo SSR e ficha técnica estruturada |
| `/comunidade` | Discussões, relatos, dúvidas e reações |
| `/comunidade/[id]` | Discussão e comentários |
| `/cadastro` | Cadastro de usuário comum |
| `/login` | Autenticação do backoffice |
| `/admin/*` | Praias, pontos, conteúdo, comunidade, anúncios, usuários, mídia e monitoramento |

## Segurança da sessão

O formulário de login chama um Route Handler do Next. Esse servidor solicita o token ao FastAPI e o grava em cookie `HttpOnly`, `SameSite=Lax` e `Secure` em produção. O JavaScript do navegador não recebe nem persiste o JWT. As chamadas administrativas passam por uma lista explícita de rotas no BFF e o FastAPI continua sendo a autoridade de autenticação e RBAC.

O proxy do Next verifica a existência da sessão para entregar a interface administrativa. Essa verificação é apenas uma melhoria de UX: toda operação sensível é novamente validada pelo back-end.

## PWA e offline

- `manifest.ts` expõe nome, cores e ícones instaláveis;
- o service worker guarda apenas o shell público e assets versionados;
- navegação pública usa estratégia network-first e cai para cache/offline;
- `/api`, `/admin` e qualquer mutação nunca são cacheados;
- mapas base e telemetria ao vivo dependem de conexão.
- discussões já abertas podem ser relidas, mas comentários e reações exigem conexão.

Atualize `CACHE_NAME` em `public/sw.js` quando a política de cache mudar.

## Executar

```bash
cd frontend
cp .env.example .env.local
npm ci
npm run dev
```

Acesse `http://localhost:3000`. Para validação completa:

```bash
npm run lint
npm run typecheck
npm test
npm run build
```

## UX e acessibilidade

O layout é mobile-first, oferece navegação inferior em telas pequenas, foco visível, link para pular ao conteúdo, avisos de risco antes de detalhes e respeito a `prefers-reduced-motion`. O score não é mostrado como certeza: a interface exibe confiança, origem, cache, motivos e ausência de dados essenciais.

Anúncios são identificados como publicidade, abrem apenas destinos HTTPS e usam `rel="sponsored nofollow noreferrer"`. Em produção, substitua o endpoint público de tiles OpenStreetMap por um provedor compatível com o volume previsto e sua política de uso.
