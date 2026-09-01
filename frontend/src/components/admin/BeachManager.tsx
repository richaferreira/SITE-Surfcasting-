"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { adminRequest, jsonRequest } from "@/lib/admin-api";
import type { Beach } from "@/lib/types";

type ManagedBeach = Beach & { is_published: boolean; created_at: string };

export function BeachManager() {
  const [items, setItems] = useState<ManagedBeach[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);

  const load = useCallback(async () => {
    try { const data = await adminRequest<{ items: ManagedBeach[] }>("beaches?limit=100"); setItems(data.items); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao carregar."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => {
    adminRequest<{ items: ManagedBeach[] }>("beaches?limit=100")
      .then((data) => setItems(data.items))
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Falha ao carregar."))
      .finally(() => setLoading(false));
  }, []);

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setMessage("");
    const form = new FormData(event.currentTarget);
    const payload = {
      name: form.get("name"), city: form.get("city"), state: "RJ",
      latitude: Number(form.get("latitude")), longitude: Number(form.get("longitude")),
      sea_bearing_deg: Number(form.get("sea_bearing_deg")), beach_profile: form.get("beach_profile"),
      accessibility_summary: form.get("accessibility_summary") || null,
      description: form.get("description") || null, is_published: form.get("is_published") === "on",
    };
    try { await adminRequest("beaches", jsonRequest("POST", payload)); event.currentTarget.reset(); setOpen(false); setMessage("Praia criada com sucesso."); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao criar."); }
  }

  async function toggle(beach: ManagedBeach) {
    setError("");
    try { await adminRequest(`beaches/${beach.id}`, jsonRequest("PATCH", { is_published: !beach.is_published })); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao atualizar."); }
  }

  async function archive(beach: ManagedBeach) {
    if (!window.confirm(`Arquivar ${beach.name}? Pontos vinculados serão preservados.`)) return;
    try { await adminRequest(`beaches/${beach.id}`, { method: "DELETE" }); setMessage("Praia arquivada."); await load(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao arquivar."); }
  }

  return (
    <section className="manager-layout">
      <div className="manager-toolbar"><div><strong>{items.length}</strong><span>praias cadastradas</span></div><button className="button primary" onClick={() => setOpen((value) => !value)}>{open ? "Fechar" : "+ Nova praia"}</button></div>
      {open && <form className="admin-form card" onSubmit={create}><div className="form-heading"><h2>Nova praia</h2><p>Coordenadas em graus decimais e direção da areia para o mar.</p></div><div className="form-grid"><label>Nome<input name="name" required minLength={3} /></label><label>Cidade<input name="city" required defaultValue="Saquarema" /></label><label>Latitude<input name="latitude" type="number" step="any" required defaultValue="-22.93" /></label><label>Longitude<input name="longitude" type="number" step="any" required defaultValue="-42.49" /></label><label>Direção do mar (°)<input name="sea_bearing_deg" type="number" min="0" max="359.9" step="0.1" required defaultValue="160" /></label><label>Perfil<select name="beach_profile"><option>TOMBO</option><option>INTERMEDIARIA</option><option>RASA</option><option>ABRIGADA</option></select></label><label className="wide">Acessibilidade<input name="accessibility_summary" maxLength={500} /></label><label className="wide">Descrição<textarea name="description" rows={4} /></label></div><label className="check-row"><input type="checkbox" name="is_published" /> Publicar imediatamente</label><button className="button primary" type="submit">Salvar praia</button></form>}
      {error && <div className="notice error" role="alert">{error}</div>}{message && <div className="notice success" role="status">{message}</div>}
      <div className="admin-table-wrap card"><table className="admin-table"><thead><tr><th>Praia</th><th>Perfil</th><th>Coordenadas</th><th>Status</th><th><span className="sr-only">Ações</span></th></tr></thead><tbody>{loading ? <tr><td colSpan={5}>Carregando…</td></tr> : items.map((beach) => <tr key={beach.id}><td><strong>{beach.name}</strong><small>{beach.city} · {beach.slug}</small></td><td>{beach.beach_profile.toLowerCase()}</td><td>{beach.latitude.toFixed(4)}, {beach.longitude.toFixed(4)}</td><td><button className={`status-button ${beach.is_published ? "published" : "draft"}`} onClick={() => toggle(beach)}>{beach.is_published ? "Publicada" : "Rascunho"}</button></td><td className="table-actions"><button onClick={() => archive(beach)} aria-label={`Arquivar ${beach.name}`}>Arquivar</button></td></tr>)}</tbody></table></div>
    </section>
  );
}
