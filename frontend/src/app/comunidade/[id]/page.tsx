import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ThreadInteractions } from "@/components/ThreadInteractions";
import { getCommunityThread } from "@/lib/api";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const id = Number((await params).id);
  const { item } = await getCommunityThread(id);
  return { title: item?.title ?? "Discussão" };
}

export default async function ThreadPage({ params }: Props) {
  const id = Number((await params).id);
  if (!Number.isInteger(id) || id < 1) notFound();
  const { item: thread, demo } = await getCommunityThread(id);
  if (!thread) notFound();
  return (
    <section className="shell thread-page">
      <Link className="back-link" href="/comunidade">← Voltar à comunidade</Link>
      <article className="thread-detail card">
        <div className="thread-meta"><span className={`community-category ${thread.category.toLowerCase()}`}>{thread.category.toLowerCase()}</span><span>{thread.beach?.name ?? "Conversa geral"}</span></div>
        <h1>{thread.title}</h1><p>{thread.content}</p>
        <div className="thread-author"><i>{thread.author.name.slice(0, 2).toUpperCase()}</i><span><strong>{thread.author.name}</strong><small>@{thread.author.username} · {new Date(thread.created_at).toLocaleString("pt-BR")}</small></span></div>
      </article>
      <ThreadInteractions thread={thread} demo={demo} />
    </section>
  );
}
