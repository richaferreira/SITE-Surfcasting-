"use client";

import { FormEvent, useState } from "react";

import { browserApi } from "../lib/api";

type Comment = {
  id: number;
  author_name: string;
  content: string;
  created_at: string;
};

type ReportTarget = { post_id?: number; comment_id?: number } | null;

export default function CommunityActions({ postId, initialLikes, initialComments }: { postId: number; initialLikes: number; initialComments: number }) {
  const [likes, setLikes] = useState(initialLikes);
  const [commentCount, setCommentCount] = useState(initialComments);
  const [comments, setComments] = useState<Comment[] | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [reportTarget, setReportTarget] = useState<ReportTarget>(null);

  async function like() {
    setMessage(null);
    try {
      await browserApi(`/api/v1/community/posts/${postId}/like`, { method: "POST" }, true);
      setLikes((value) => value + 1);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Não foi possível curtir.");
    }
  }

  async function toggleComments() {
    if (comments) {
      setComments(null);
      return;
    }
    try {
      setComments(await browserApi<Comment[]>(`/api/v1/community/posts/${postId}/comments`));
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Não foi possível carregar os comentários.");
    }
  }

  async function comment(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const content = String(form.get("content") ?? "").trim();
    if (!content) return;
    try {
      const created = await browserApi<Comment>(`/api/v1/community/posts/${postId}/comments`, {
        method: "POST",
        body: JSON.stringify({ content }),
      }, true);
      setComments((items) => [...(items ?? []), created]);
      setCommentCount((value) => value + 1);
      event.currentTarget.reset();
      setMessage(null);
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Não foi possível comentar.");
    }
  }

  async function report(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!reportTarget) return;
    const form = new FormData(event.currentTarget);
    try {
      await browserApi("/api/v1/reports", {
        method: "POST",
        body: JSON.stringify({
          ...reportTarget,
          reason: form.get("reason"),
          details: form.get("details") || null,
        }),
      }, true);
      setReportTarget(null);
      setMessage("Denúncia enviada para análise da moderação.");
    } catch (err) {
      setMessage(err instanceof Error ? err.message : "Não foi possível enviar a denúncia.");
    }
  }

  return (
    <div className="communityActions">
      <div className="actionRow">
        <button className="textButton" type="button" onClick={like}>♥ {likes}</button>
        <button className="textButton" type="button" onClick={toggleComments}>Comentários {commentCount}</button>
        <button className="textButton reportButton" type="button" onClick={() => setReportTarget({ post_id: postId })}>Denunciar publicação</button>
      </div>
      {message ? <small className="communityMessage">{message}</small> : null}
      {reportTarget ? (
        <form className="reportForm" onSubmit={report}>
          <select name="reason" defaultValue="SPAM" aria-label="Motivo da denúncia">
            <option value="SPAM">Spam</option>
            <option value="ABUSO">Abuso ou assédio</option>
            <option value="CONTEUDO_IMPROPRIO">Conteúdo impróprio</option>
            <option value="DESINFORMACAO">Desinformação</option>
            <option value="OUTRO">Outro</option>
          </select>
          <textarea name="details" maxLength={1000} rows={2} placeholder="Explique o problema (opcional)" />
          <div className="actionRow">
            <button className="secondaryButton" type="submit">Enviar denúncia</button>
            <button className="textButton" type="button" onClick={() => setReportTarget(null)}>Cancelar</button>
          </div>
        </form>
      ) : null}
      {comments ? (
        <div className="commentsBox">
          {comments.map((item) => (
            <div className="comment" key={item.id}>
              <strong>{item.author_name}</strong>
              <p>{item.content}</p>
              <button className="textButton reportButton" type="button" onClick={() => setReportTarget({ comment_id: item.id })}>Denunciar comentário</button>
            </div>
          ))}
          <form className="inlineComment" onSubmit={comment}>
            <input name="content" placeholder="Escreva um comentário" minLength={2} required />
            <button type="submit">Enviar</button>
          </form>
        </div>
      ) : null}
    </div>
  );
}
