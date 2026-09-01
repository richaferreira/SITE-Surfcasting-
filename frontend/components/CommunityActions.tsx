"use client";

import { FormEvent, useState } from "react";

import { browserApi } from "../lib/api";

type Comment = {
  id: number;
  author_name: string;
  content: string;
  created_at: string;
};

export default function CommunityActions({ postId, initialLikes, initialComments }: { postId: number; initialLikes: number; initialComments: number }) {
  const [likes, setLikes] = useState(initialLikes);
  const [commentCount, setCommentCount] = useState(initialComments);
  const [comments, setComments] = useState<Comment[] | null>(null);
  const [message, setMessage] = useState<string | null>(null);

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

  return (
    <div className="communityActions">
      <div className="actionRow">
        <button className="textButton" type="button" onClick={like}>♥ {likes}</button>
        <button className="textButton" type="button" onClick={toggleComments}>Comentários {commentCount}</button>
      </div>
      {message ? <small className="riskText">{message}</small> : null}
      {comments ? (
        <div className="commentsBox">
          {comments.map((item) => (
            <div className="comment" key={item.id}><strong>{item.author_name}</strong><p>{item.content}</p></div>
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
