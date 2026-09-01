"use client";

import { useCallback, useEffect, useState } from "react";
import { adminRequest, jsonRequest } from "@/lib/admin-api";

type Thread = { id: number; title: string; category: string; status: "PUBLICADO" | "OCULTO" | "ARQUIVADO"; author: { name: string; username: string }; comment_count: number; reaction_count: number; created_at: string };

export function CommunityModeration() {
  const [items, setItems] = useState<Thread[]>([]); const [error, setError] = useState("");
  const load = useCallback(async () => { try { setItems((await adminRequest<{ items: Thread[] }>("community/threads?limit=100")).items); } catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao carregar discussões."); } }, []);
  useEffect(() => { adminRequest<{ items: Thread[] }>("community/threads?limit=100").then((data) => setItems(data.items)).catch((reason) => setError(reason instanceof Error ? reason.message : "Falha ao carregar discussões.")); }, []);
  async function setStatus(thread: Thread, status: Thread["status"]) { try { await adminRequest(`community/threads/${thread.id}`, jsonRequest("PATCH", { status })); await load(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao moderar."); } }
  return <section className="manager-layout">{error && <div className="notice error">{error}</div>}<div className="admin-table-wrap card"><table className="admin-table"><thead><tr><th>Discussão</th><th>Categoria</th><th>Interações</th><th>Status</th><th>Moderação</th></tr></thead><tbody>{items.length === 0 ? <tr><td colSpan={5}>Nenhuma discussão.</td></tr> : items.map((thread) => <tr key={thread.id}><td><strong>{thread.title}</strong><small>@{thread.author.username} · {new Date(thread.created_at).toLocaleDateString("pt-BR")}</small></td><td>{thread.category.toLowerCase()}</td><td>{thread.reaction_count} apoios · {thread.comment_count} comentários</td><td><span className={`status-button ${thread.status === "PUBLICADO" ? "published" : "draft"}`}>{thread.status.toLowerCase()}</span></td><td className="moderation-actions"><button onClick={() => setStatus(thread, "PUBLICADO")}>Publicar</button><button onClick={() => setStatus(thread, "OCULTO")}>Ocultar</button><button onClick={() => setStatus(thread, "ARQUIVADO")}>Arquivar</button></td></tr>)}</tbody></table></div></section>;
}
