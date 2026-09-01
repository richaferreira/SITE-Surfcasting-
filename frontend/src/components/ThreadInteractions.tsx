"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import type { CommunityComment, CommunityThread } from "@/lib/types";

export function ThreadInteractions({ thread, demo }: { thread: CommunityThread; demo: boolean }) {
  const [comments, setComments] = useState<CommunityComment[]>(thread.comments ?? []);
  const [reactions, setReactions] = useState(thread.reaction_count);
  const [error, setError] = useState("");
  const [sending, setSending] = useState(false);

  async function react() {
    if (demo) { setError("Discussões demonstrativas não recebem reações."); return; }
    setError("");
    const response = await fetch(`/api/community/threads/${thread.id}/reactions`, { method: "POST" });
    const data = await response.json();
    if (response.status === 401) setError("Entre para apoiar uma discussão.");
    else if (!response.ok) setError(data.detail ?? "Falha ao reagir.");
    else setReactions(data.reaction_count);
  }

  async function comment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (demo) { setError("Discussões demonstrativas não recebem comentários."); return; }
    setSending(true); setError("");
    const form = new FormData(event.currentTarget);
    const response = await fetch(`/api/community/threads/${thread.id}/comments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ content: form.get("content") }),
    });
    const data = await response.json();
    if (response.status === 401) setError("Entre para comentar.");
    else if (!response.ok) setError(data.detail ?? "Falha ao comentar.");
    else { setComments((current) => [...current, data]); event.currentTarget.reset(); }
    setSending(false);
  }

  return (
    <div className="thread-interactions">
      <div className="reaction-row"><button className="button secondary" onClick={react}>♡ Apoiar · {reactions}</button><span>Informação útil? Apoie para dar visibilidade.</span></div>
      {error && <div className="notice error">{error} <Link href="/login">Entrar</Link></div>}
      <section className="comment-section">
        <h2>{comments.length} comentários</h2>
        {comments.map((item) => <article className="comment card" key={item.id}><i>{item.author.name.slice(0, 2).toUpperCase()}</i><div><strong>{item.author.name}</strong><small>@{item.author.username} · {new Date(item.created_at).toLocaleString("pt-BR")}</small><p>{item.content}</p></div></article>)}
        <form className="comment-form card" onSubmit={comment}><label>Contribua para a discussão<textarea name="content" required minLength={2} maxLength={2000} rows={4} placeholder="Inclua contexto e priorize segurança." /></label><button className="button primary" disabled={sending}>{sending ? "Publicando…" : "Publicar comentário"}</button></form>
      </section>
    </div>
  );
}
