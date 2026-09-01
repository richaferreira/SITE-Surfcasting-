import Link from "next/link";

const modules = [
  ["Praias", "Publique perfis, coordenadas e orientações de acesso.", "/admin/praias", "≈"],
  ["Pontos técnicos", "Mapeie canais, coroas, valas e riscos.", "/admin/pontos", "⌖"],
  ["Academia", "Produza e revise conteúdos e fichas de equipamentos.", "/admin/conteudos", "◇"],
  ["Gestor de mídia", "Otimize imagens e vídeos para conexões móveis.", "/admin/midia", "▧"],
  ["Comunidade", "Modere discussões, comentários e convivência.", "/admin/comunidade", "◌"],
  ["Anúncios", "Controle campanhas, períodos e posicionamentos.", "/admin/anuncios", "▤"],
] as const;

export default function AdminPage() {
  return (
    <>
      <header className="admin-page-header"><div><span className="eyebrow">Operação</span><h1>Visão geral</h1><p>Gerencie o portal sem perder de vista qualidade, segurança e experiência do pescador.</p></div><Link className="button secondary" href="/">Ver site público ↗</Link></header>
      <section className="admin-kpis">
        <article className="admin-kpi card"><span>Status do portal</span><strong><i className="live-dot" /> Operacional</strong><small>Validação final ocorre no servidor</small></article>
        <article className="admin-kpi card"><span>Conteúdo</span><strong>Workflow RBAC</strong><small>Autor → revisão → publicação</small></article>
        <article className="admin-kpi card"><span>Telemetria</span><strong>3 provedores</strong><small>Stormglass, OpenWeather e maré</small></article>
      </section>
      <section className="admin-module-grid">
        {modules.map(([title, description, href, icon]) => <Link className="admin-module card" href={href} key={href}><i aria-hidden="true">{icon}</i><div><h2>{title}</h2><p>{description}</p><span>Abrir módulo →</span></div></Link>)}
      </section>
      <section className="admin-guidance card"><span className="eyebrow">Boas práticas</span><h2>Publique para quem está com sinal instável e atenção dividida.</h2><ul><li>Descrições curtas e acionáveis.</li><li>Riscos visíveis antes dos detalhes.</li><li>Imagens comprimidas e pontos verificados.</li></ul></section>
    </>
  );
}
