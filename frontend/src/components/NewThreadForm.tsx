"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";
import type { Beach } from "@/lib/types";

export function NewThreadForm({ beaches }: { beaches: Beach[] }) {
  const router = useRouter();
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true); setError("");
    const form = new FormData(event.currentTarget);
    const beach = Number(form.get("beach_id"));
    const response = await fetch("/api/community/threads", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: form.get("title"),
        content: form.get("content"),
        category: form.get("category"),
        beach_id: beach || null,
      }),
    });
    const data = await response.json();
    if (!response.ok) { setError(data.detail ?? "Não foi possível publicar."); setLoading(false); return; }
    router.push(`/comunidade/${data.id}`);
    router.refresh();
  }

  return (
    <form className="new-thread-form card" onSubmit={submit}>
      <label>Título<input name="title" required minLength={5} maxLength={160} /></label>
      <div className="form-grid"><label>Categoria<select name="category"><option value="RELATO">Relato</option><option value="DUVIDA">Dúvida</option><option value="CAPTURA">Captura</option><option value="EQUIPAMENTO">Equipamento</option></select></label><label>Praia relacionada<select name="beach_id"><option value="">Conversa geral</option>{beaches.map((beach) => <option value={beach.id} key={beach.id}>{beach.name}</option>)}</select></label></div>
      <label>Relato ou pergunta<textarea name="content" required minLength={10} maxLength={5000} rows={10} placeholder="Condições, horário, observações e cuidados…" /></label>
      {error && <div className="notice error">{error}</div>}
      <button className="button primary" disabled={loading}>{loading ? "Publicando…" : "Publicar discussão"}</button>
    </form>
  );
}
