"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { adminRequest, jsonRequest } from "@/lib/admin-api";

type ManagedPost = { id: number; title: string; slug: string; content_type: string; status: string; updated_at: string; author: { name: string } };

export function ContentManager() {
  const [items, setItems] = useState<ManagedPost[]>([]);
  const [open, setOpen] = useState(false);
  const [contentType, setContentType] = useState("ARTIGO");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const load = useCallback(async () => { try { setItems((await adminRequest<{ items: ManagedPost[] }>("posts?limit=100")).items); } catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao carregar."); } }, []);
  useEffect(() => {
    adminRequest<{ items: ManagedPost[] }>("posts?limit=100")
      .then((data) => setItems(data.items))
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Falha ao carregar."));
  }, []);

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setMessage(""); const form = new FormData(event.currentTarget);
    const equipment = contentType === "EQUIPAMENTO" ? {
      rod_length_m: Number(form.get("rod_length_m")) || null, rod_construction: form.get("rod_construction") || null,
      reel_size: Number(form.get("reel_size")) || null, main_line_material: form.get("main_line_material") || null,
      main_line_diameter_mm: Number(form.get("main_line_diameter_mm")) || null, shock_leader_type: form.get("shock_leader_type") || null,
      casting_weight_min_g: Number(form.get("casting_weight_min_g")) || null, casting_weight_max_g: Number(form.get("casting_weight_max_g")) || null,
    } : null;
    const payload = { title: form.get("title"), excerpt: form.get("excerpt") || null, content: form.get("content"), content_type: contentType, status: form.get("status"), seo_title: form.get("seo_title") || null, seo_description: form.get("seo_description") || null, equipment_specification: equipment };
    try { await adminRequest("posts", jsonRequest("POST", payload)); event.currentTarget.reset(); setOpen(false); setMessage("Conteúdo criado."); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao criar."); }
  }

  async function archive(post: ManagedPost) { if (!window.confirm(`Arquivar “${post.title}”?`)) return; try { await adminRequest(`posts/${post.id}`, { method: "DELETE" }); await load(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao arquivar."); } }

  return <section className="manager-layout">
    <div className="manager-toolbar"><div><strong>{items.length}</strong><span>itens editoriais</span></div><button className="button primary" onClick={() => setOpen((value) => !value)}>{open ? "Fechar editor" : "+ Novo conteúdo"}</button></div>
    {open && <form className="admin-form card" onSubmit={create}><div className="form-heading"><h2>Novo conteúdo</h2><p>Use Markdown simples. O site renderiza o texto sem HTML arbitrário.</p></div><div className="form-grid"><label className="wide">Título<input name="title" required minLength={5} maxLength={220} /></label><label>Tipo<select value={contentType} onChange={(event) => setContentType(event.target.value)}><option>ARTIGO</option><option>TUTORIAL</option><option>VIDEO</option><option>EQUIPAMENTO</option></select></label><label>Status<select name="status"><option value="RASCUNHO">Rascunho</option><option value="EM_REVISAO">Em revisão</option><option value="PUBLICADO">Publicado (Admin)</option></select></label><label className="wide">Resumo<textarea name="excerpt" rows={2} maxLength={500} /></label><label className="wide">Conteúdo em Markdown<textarea name="content" rows={12} required minLength={20} /></label><label>Título SEO<input name="seo_title" maxLength={70} /></label><label>Descrição SEO<input name="seo_description" maxLength={160} /></label>{contentType === "EQUIPAMENTO" && <><label>Vara (m)<input name="rod_length_m" type="number" step="0.1" defaultValue="4.5" /></label><label>Construção<input name="rod_construction" defaultValue="Tubular" /></label><label>Molinete<input name="reel_size" type="number" defaultValue="9000" /></label><label>Linha<input name="main_line_material" defaultValue="Monofilamento" /></label><label>Diâmetro (mm)<input name="main_line_diameter_mm" type="number" step="0.01" defaultValue="0.18" /></label><label>Shock leader<input name="shock_leader_type" defaultValue="Cônico" /></label><label>Peso mínimo (g)<input name="casting_weight_min_g" type="number" /></label><label>Peso máximo (g)<input name="casting_weight_max_g" type="number" /></label></>}</div><button className="button primary">Salvar conteúdo</button></form>}
    {error && <div className="notice error">{error}</div>}{message && <div className="notice success">{message}</div>}
    <div className="admin-table-wrap card"><table className="admin-table"><thead><tr><th>Conteúdo</th><th>Tipo</th><th>Status</th><th>Autor</th><th><span className="sr-only">Ações</span></th></tr></thead><tbody>{items.length === 0 ? <tr><td colSpan={5}>Nenhum conteúdo criado.</td></tr> : items.map((post) => <tr key={post.id}><td><strong>{post.title}</strong><small>{post.slug}</small></td><td>{post.content_type.toLowerCase()}</td><td><span className={`status-button ${post.status === "PUBLICADO" ? "published" : "draft"}`}>{post.status.toLowerCase().replaceAll("_", " ")}</span></td><td>{post.author.name}</td><td className="table-actions"><button onClick={() => archive(post)}>Arquivar</button></td></tr>)}</tbody></table></div>
  </section>;
}
