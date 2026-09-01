import type { Metadata } from "next";
import Link from "next/link";
import { getCommunityThreads } from "@/lib/api";

export const metadata: Metadata = {
  title: "Comunidade",
  description: "Relatos, dúvidas e conhecimento local sobre surfcasting na Região dos Lagos.",
};

const labels = { RELATO: "Relato", DUVIDA: "Dúvida", CAPTURA: "Captura", EQUIPAMENTO: "Equipamento" };

export default async function CommunityPage() {
  const { items, demo } = await getCommunityThreads();
  return (
    <>
      <section className="community-hero">
        <div className="shell community-head">
          <div><span className="eyebrow">Comunidade local</span><h1>Experiência compartilhada.<br /><em>Mar mais bem lido.</em></h1><p>Troque informações sem transformar referência em promessa. Estruturas mudam, segurança não.</p></div>
          <Link className="button primary" href="/comunidade/nova">+ Iniciar discussão</Link>
        </div>
      </section>
      <section className="shell community-layout">
        <main className="thread-feed">
          {demo && <div className="notice info">Discussões demonstrativas enquanto a comunidade recebe as primeiras publicações.</div>}
          {items.map((thread) => (
            <Link className="thread-card card" href={`/comunidade/${thread.id}`} key={thread.id}>
              <div className="thread-avatar">{thread.author.name.slice(0, 2).toUpperCase()}</div>
              <div>
                <div className="thread-meta"><span className={`community-category ${thread.category.toLowerCase()}`}>{labels[thread.category]}</span><span>{thread.beach?.name ?? "Conversa geral"}</span><span>{new Date(thread.created_at).toLocaleDateString("pt-BR")}</span></div>
                <h2>{thread.title}</h2><p>{thread.content}</p>
                <footer><span>♡ {thread.reaction_count}</span><span>◌ {thread.comment_count} comentários</span><strong>{thread.author.name}</strong></footer>
              </div>
            </Link>
          ))}
        </main>
        <aside className="community-rules card"><span className="eyebrow">Código da praia</span><h2>Contribua com contexto.</h2><ol><li>Informe maré, vento e horário.</li><li>Não incentive entrada em canais.</li><li>Proteja locais sensíveis e respeite defesos.</li><li>Discuta ideias, não pessoas.</li></ol><Link href="/academia">Revisar fundamentos →</Link></aside>
      </section>
    </>
  );
}
