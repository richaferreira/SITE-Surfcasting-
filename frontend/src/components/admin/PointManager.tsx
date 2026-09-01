"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { adminRequest, jsonRequest } from "@/lib/admin-api";
import type { Beach, FishingPoint } from "@/lib/types";

type ManagedPoint = FishingPoint & { is_active: boolean; beach_id: number };

export function PointManager() {
  const [beaches, setBeaches] = useState<Beach[]>([]);
  const [beachId, setBeachId] = useState(0);
  const [items, setItems] = useState<ManagedPoint[]>([]);
  const [open, setOpen] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const loadPoints = useCallback(async (id: number) => {
    if (!id) return;
    try { const data = await adminRequest<{ items: ManagedPoint[] }>(`beaches/${id}/points`); setItems(data.items); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao carregar pontos."); }
  }, []);

  useEffect(() => {
    adminRequest<{ items: Beach[] }>("beaches?limit=100").then((data) => {
      setBeaches(data.items); const first = data.items[0]?.id ?? 0; setBeachId(first); void loadPoints(first);
    }).catch((reason) => setError(reason instanceof Error ? reason.message : "Falha ao carregar praias."));
  }, [loadPoints]);

  async function create(event: FormEvent<HTMLFormElement>) {
    event.preventDefault(); setError(""); setMessage("");
    const form = new FormData(event.currentTarget);
    const payload = {
      name: form.get("name"), point_type: form.get("point_type"), description: form.get("description") || null,
      latitude: Number(form.get("latitude")), longitude: Number(form.get("longitude")), accessibility: form.get("accessibility"),
      access_notes: form.get("access_notes") || null, risk_notes: form.get("risk_notes") || null,
      verified_at: new Date().toISOString(), is_active: true,
    };
    try { await adminRequest(`beaches/${beachId}/points`, jsonRequest("POST", payload)); event.currentTarget.reset(); setOpen(false); setMessage("Ponto criado."); await loadPoints(beachId); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao criar ponto."); }
  }

  async function archive(point: ManagedPoint) {
    if (!window.confirm(`Arquivar ${point.name}?`)) return;
    try { await adminRequest(`points/${point.id}`, { method: "DELETE" }); setMessage("Ponto arquivado."); await loadPoints(beachId); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao arquivar."); }
  }

  return <section className="manager-layout">
    <div className="manager-toolbar"><label>Praia<select value={beachId} onChange={(event) => { const id = Number(event.target.value); setBeachId(id); void loadPoints(id); }}>{beaches.map((beach) => <option value={beach.id} key={beach.id}>{beach.name}</option>)}</select></label><button className="button primary" onClick={() => setOpen((value) => !value)}>{open ? "Fechar" : "+ Novo ponto"}</button></div>
    {open && <form className="admin-form card" onSubmit={create}><div className="form-heading"><h2>Novo ponto técnico</h2><p>Evite nomes definitivos para estruturas que se deslocam com frequência.</p></div><div className="form-grid"><label>Nome<input name="name" required minLength={3} /></label><label>Tipo<select name="point_type"><option value="BURACO">Buraco / vala</option><option value="COROA_AREIA">Coroa de areia</option><option value="CANAL_RETORNO">Canal de retorno</option><option value="ESTRUTURA">Estrutura</option><option value="OUTRO">Outro</option></select></label><label>Latitude<input name="latitude" type="number" step="any" required /></label><label>Longitude<input name="longitude" type="number" step="any" required /></label><label>Acessibilidade<select name="accessibility"><option value="FACIL">Fácil</option><option value="MODERADA">Moderada</option><option value="DIFICIL">Difícil</option><option value="RESTRITA">Restrita</option></select></label><label className="wide">Descrição<textarea name="description" rows={3} /></label><label>Acesso<input name="access_notes" maxLength={500} /></label><label>Riscos<input name="risk_notes" maxLength={500} /></label></div><button className="button primary">Salvar ponto</button></form>}
    {error && <div className="notice error">{error}</div>}{message && <div className="notice success">{message}</div>}
    <div className="admin-table-wrap card"><table className="admin-table"><thead><tr><th>Ponto</th><th>Tipo</th><th>Acesso</th><th>Verificação</th><th><span className="sr-only">Ações</span></th></tr></thead><tbody>{items.length === 0 ? <tr><td colSpan={5}>Nenhum ponto nesta praia.</td></tr> : items.map((point) => <tr key={point.id}><td><strong>{point.name}</strong><small>{point.latitude.toFixed(4)}, {point.longitude.toFixed(4)}</small></td><td>{point.point_type.toLowerCase().replaceAll("_", " ")}</td><td>{point.accessibility.toLowerCase()}</td><td>{point.verified_at ? new Date(point.verified_at).toLocaleDateString("pt-BR") : "Pendente"}</td><td className="table-actions"><button onClick={() => archive(point)}>Arquivar</button></td></tr>)}</tbody></table></div>
  </section>;
}
