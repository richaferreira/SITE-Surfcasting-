"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { adminRequest } from "@/lib/admin-api";

type Asset = { id: number; kind: "IMAGE" | "VIDEO"; original_name: string; mime_type: string; url: string; original_size_bytes: number; size_bytes: number; width: number | null; height: number | null; duration_seconds: number | null; created_at: string };
const size = (bytes: number) => bytes < 1024 * 1024 ? `${Math.round(bytes / 1024)} KB` : `${(bytes / 1024 / 1024).toFixed(1)} MB`;

export function MediaManager() {
  const [items, setItems] = useState<Asset[]>([]); const [error, setError] = useState(""); const [message, setMessage] = useState(""); const [uploading, setUploading] = useState(false);
  const load = useCallback(async () => { try { setItems((await adminRequest<{ items: Asset[] }>("media?limit=100")).items); } catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao carregar mídia."); } }, []);
  useEffect(() => {
    adminRequest<{ items: Asset[] }>("media?limit=100")
      .then((data) => setItems(data.items))
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Falha ao carregar mídia."));
  }, []);
  async function upload(event: FormEvent<HTMLFormElement>) { event.preventDefault(); setUploading(true); setError(""); setMessage(""); const data = new FormData(event.currentTarget); try { await adminRequest("media", { method: "POST", body: data }); event.currentTarget.reset(); setMessage("Arquivo processado e publicado."); await load(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Falha no upload."); } finally { setUploading(false); } }
  return <section className="manager-layout">
    <form className="upload-zone card" onSubmit={upload}><div className="upload-icon" aria-hidden="true">↑</div><div><h2>Envie uma imagem ou vídeo</h2><p>JPG, PNG, WebP, MP4, MOV ou WebM. O servidor valida e recomprime o arquivo.</p></div><label className="button secondary">Selecionar arquivo<input className="sr-only" name="file" type="file" accept="image/jpeg,image/png,image/webp,video/mp4,video/quicktime,video/webm" required /></label><button className="button primary" disabled={uploading}>{uploading ? "Processando…" : "Enviar e otimizar"}</button></form>
    {error && <div className="notice error">{error}</div>}{message && <div className="notice success">{message}</div>}
    <div className="media-grid">{items.length === 0 ? <div className="empty-card card">Nenhuma mídia enviada.</div> : items.map((asset) => <article className="media-card card" key={asset.id}><div className={`media-preview ${asset.kind.toLowerCase()}`}><span>{asset.kind === "IMAGE" ? "▧" : "▶"}</span></div><div><strong>{asset.original_name}</strong><small>{asset.width && asset.height ? `${asset.width} × ${asset.height}` : asset.duration_seconds ? `${asset.duration_seconds}s` : asset.mime_type}</small><div className="compression"><span>{size(asset.original_size_bytes)}</span><b>→</b><strong>{size(asset.size_bytes)}</strong></div><a href={asset.url} target="_blank" rel="noreferrer">Abrir arquivo ↗</a></div></article>)}</div>
  </section>;
}
