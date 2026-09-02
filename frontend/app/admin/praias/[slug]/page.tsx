"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";

import SiteHeader from "../../../../components/SiteHeader";
import { browserApi } from "../../../../lib/api";

type Point = {
  id: number;
  praia_id: number;
  name: string;
  slug: string;
  point_type: string;
  description: string | null;
  latitude: number;
  longitude: number;
  accessibility: string;
  access_notes: string | null;
  risk_notes: string | null;
  is_active: boolean;
};

type Beach = {
  id: number;
  name: string;
  slug: string;
  city: string;
  state: string;
  description: string | null;
  latitude: number;
  longitude: number;
  sea_bearing_deg: number;
  beach_profile: string;
  accessibility_summary: string | null;
  is_published: boolean;
  points: Point[];
};

function optionalText(form: FormData, key: string) {
  const value = String(form.get(key) ?? "").trim();
  return value || null;
}

export default function ManageBeachPage() {
  const params = useParams<{ slug: string }>();
  const slug = decodeURIComponent(params.slug);
  const [beach, setBeach] = useState<Beach | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const data = await browserApi<Beach>(`/api/v1/beaches/${encodeURIComponent(slug)}/manage`, {}, true);
      setBeach(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível carregar a praia.");
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => { void load(); }, [load]);

  async function updateBeach(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!beach) return;
    setError(null); setSuccess(null);
    const form = new FormData(event.currentTarget);
    try {
      const updated = await browserApi<Beach>(`/api/v1/beaches/${encodeURIComponent(beach.slug)}`, {
        method: "PATCH",
        body: JSON.stringify({
          name: form.get("name"),
          slug: form.get("slug"),
          city: form.get("city"),
          state: form.get("state"),
          description: optionalText(form, "description"),
          latitude: Number(form.get("latitude")),
          longitude: Number(form.get("longitude")),
          sea_bearing_deg: Number(form.get("sea_bearing_deg")),
          beach_profile: form.get("beach_profile"),
          accessibility_summary: optionalText(form, "accessibility_summary"),
          is_published: form.get("is_published") === "on",
        }),
      }, true);
      setSuccess("Praia atualizada.");
      if (updated.slug !== beach.slug) {
        window.location.href = `/admin/praias/${encodeURIComponent(updated.slug)}`;
        return;
      }
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível atualizar a praia.");
    }
  }

  async function deleteBeach() {
    if (!beach || !window.confirm(`Excluir definitivamente ${beach.name}?`)) return;
    try {
      await browserApi(`/api/v1/beaches/${encodeURIComponent(beach.slug)}`, { method: "DELETE" }, true);
      window.location.href = "/admin";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível excluir a praia.");
    }
  }

  async function createPoint(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!beach) return;
    const form = new FormData(event.currentTarget);
    setError(null); setSuccess(null);
    try {
      await browserApi(`/api/v1/beaches/${encodeURIComponent(beach.slug)}/points`, {
        method: "POST",
        body: JSON.stringify({
          name: form.get("name"),
          slug: form.get("slug"),
          point_type: form.get("point_type"),
          description: optionalText(form, "description"),
          latitude: Number(form.get("latitude")),
          longitude: Number(form.get("longitude")),
          accessibility: form.get("accessibility"),
          access_notes: optionalText(form, "access_notes"),
          risk_notes: optionalText(form, "risk_notes"),
        }),
      }, true);
      event.currentTarget.reset();
      setSuccess("Ponto cadastrado.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível cadastrar o ponto.");
    }
  }

  async function updatePoint(event: FormEvent<HTMLFormElement>, point: Point) {
    event.preventDefault();
    if (!beach) return;
    const form = new FormData(event.currentTarget);
    try {
      await browserApi(`/api/v1/beaches/${encodeURIComponent(beach.slug)}/points/${point.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          name: form.get("name"),
          slug: form.get("slug"),
          point_type: form.get("point_type"),
          description: optionalText(form, "description"),
          latitude: Number(form.get("latitude")),
          longitude: Number(form.get("longitude")),
          accessibility: form.get("accessibility"),
          access_notes: optionalText(form, "access_notes"),
          risk_notes: optionalText(form, "risk_notes"),
          is_active: form.get("is_active") === "on",
        }),
      }, true);
      setSuccess(`Ponto ${point.name} atualizado.`);
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível atualizar o ponto.");
    }
  }

  async function deletePoint(point: Point) {
    if (!beach || !window.confirm(`Excluir o ponto ${point.name}?`)) return;
    try {
      await browserApi(`/api/v1/beaches/${encodeURIComponent(beach.slug)}/points/${point.id}`, { method: "DELETE" }, true);
      setSuccess("Ponto excluído.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível excluir o ponto.");
    }
  }

  return (
    <main>
      <SiteHeader />
      <section className="pageShell">
        <div className="pageHeading">
          <span className="eyebrow">Backoffice · geografia</span>
          <h1>{loading ? "Carregando..." : beach?.name ?? "Praia"}</h1>
          <p>Edite os dados públicos e mantenha canais, buracos, coroas e estruturas atualizados.</p>
        </div>
        {error ? <div className="notice errorNotice">{error}</div> : null}
        {success ? <div className="notice successNotice">{success}</div> : null}

        {beach ? (
          <>
            <article className="panel adminEditor">
              <div className="panelHeading"><div><span className="eyebrow">Praia</span><h2>Dados principais</h2></div><button className="dangerButton" type="button" onClick={() => void deleteBeach()}>Excluir praia</button></div>
              <form className="formStack" onSubmit={updateBeach}>
                <div className="formGrid"><label>Nome<input name="name" defaultValue={beach.name} required /></label><label>Slug<input name="slug" defaultValue={beach.slug} pattern="[a-z0-9-]+" required /></label><label>Cidade<input name="city" defaultValue={beach.city} required /></label><label>UF<input name="state" defaultValue={beach.state} maxLength={2} required /></label></div>
                <label>Descrição<textarea name="description" rows={4} defaultValue={beach.description ?? ""} /></label>
                <div className="formGrid"><label>Latitude<input name="latitude" type="number" step="0.000001" defaultValue={beach.latitude} required /></label><label>Longitude<input name="longitude" type="number" step="0.000001" defaultValue={beach.longitude} required /></label><label>Direção para o mar (°)<input name="sea_bearing_deg" type="number" min="0" max="359.99" step="0.01" defaultValue={beach.sea_bearing_deg} required /></label><label>Perfil<select name="beach_profile" defaultValue={beach.beach_profile}><option value="TOMBO">Tombo</option><option value="INTERMEDIARIA">Intermediária</option><option value="RASA">Rasa</option><option value="ABRIGADA">Abrigada</option></select></label></div>
                <label>Acesso<input name="accessibility_summary" defaultValue={beach.accessibility_summary ?? ""} /></label>
                <label className="checkboxLabel"><input name="is_published" type="checkbox" defaultChecked={beach.is_published} /> Publicada no portal</label>
                <button className="primaryButton formButton" type="submit">Salvar alterações</button>
              </form>
            </article>

            <div className="twoColumn adminSpotColumns">
              <article className="panel">
                <span className="eyebrow">Novo spot</span><h2>Cadastrar ponto</h2>
                <form className="formStack" onSubmit={createPoint}>
                  <label>Nome<input name="name" required /></label><label>Slug<input name="slug" required pattern="[a-z0-9-]+" /></label>
                  <div className="formGrid"><label>Tipo<select name="point_type" defaultValue="CANAL_RETORNO"><option value="BURACO">Buraco</option><option value="COROA_AREIA">Coroa de areia</option><option value="CANAL_RETORNO">Canal de retorno</option><option value="ESTRUTURA">Estrutura</option><option value="OUTRO">Outro</option></select></label><label>Acesso<select name="accessibility" defaultValue="MODERADA"><option value="FACIL">Fácil</option><option value="MODERADA">Moderada</option><option value="DIFICIL">Difícil</option><option value="RESTRITA">Restrita</option></select></label><label>Latitude<input name="latitude" type="number" step="0.000001" defaultValue={beach.latitude} required /></label><label>Longitude<input name="longitude" type="number" step="0.000001" defaultValue={beach.longitude} required /></label></div>
                  <label>Descrição<textarea name="description" rows={3} /></label><label>Notas de acesso<input name="access_notes" /></label><label>Riscos<input name="risk_notes" /></label>
                  <button className="primaryButton formButton" type="submit">Adicionar ponto</button>
                </form>
              </article>

              <article className="panel">
                <span className="eyebrow">Spots existentes</span><h2>{beach.points.length} ponto(s)</h2>
                <div className="spotEditorList">
                  {beach.points.map((point) => (
                    <details className="spotEditor" key={point.id}>
                      <summary><span><strong>{point.name}</strong><small>{point.point_type.replaceAll("_", " ")} · {point.is_active ? "ativo" : "inativo"}</small></span><span>Editar</span></summary>
                      <form className="formStack" onSubmit={(event) => void updatePoint(event, point)}>
                        <div className="formGrid"><label>Nome<input name="name" defaultValue={point.name} required /></label><label>Slug<input name="slug" defaultValue={point.slug} required pattern="[a-z0-9-]+" /></label><label>Tipo<select name="point_type" defaultValue={point.point_type}><option value="BURACO">Buraco</option><option value="COROA_AREIA">Coroa</option><option value="CANAL_RETORNO">Canal</option><option value="ESTRUTURA">Estrutura</option><option value="OUTRO">Outro</option></select></label><label>Acesso<select name="accessibility" defaultValue={point.accessibility}><option value="FACIL">Fácil</option><option value="MODERADA">Moderada</option><option value="DIFICIL">Difícil</option><option value="RESTRITA">Restrita</option></select></label><label>Latitude<input name="latitude" type="number" step="0.000001" defaultValue={point.latitude} required /></label><label>Longitude<input name="longitude" type="number" step="0.000001" defaultValue={point.longitude} required /></label></div>
                        <label>Descrição<textarea name="description" rows={2} defaultValue={point.description ?? ""} /></label><label>Notas de acesso<input name="access_notes" defaultValue={point.access_notes ?? ""} /></label><label>Riscos<input name="risk_notes" defaultValue={point.risk_notes ?? ""} /></label><label className="checkboxLabel"><input name="is_active" type="checkbox" defaultChecked={point.is_active} /> Ativo no mapa público</label>
                        <div className="formActions"><button className="primaryButton formButton" type="submit">Salvar ponto</button><button className="dangerButton" type="button" onClick={() => void deletePoint(point)}>Excluir</button></div>
                      </form>
                    </details>
                  ))}
                  {!beach.points.length ? <p className="muted">Nenhum ponto cadastrado.</p> : null}
                </div>
              </article>
            </div>
          </>
        ) : null}
      </section>
    </main>
  );
}
