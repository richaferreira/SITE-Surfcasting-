"use client";

import { useCallback, useEffect, useState } from "react";
import { adminRequest } from "@/lib/admin-api";

type Provider = { requests: number; successes: number; failures: number; success_rate_percentage: number; average_latency_ms: number; last_status_code: number | null; last_error_code: string | null; last_called_at: string | null };
type Summary = { started_at: string; traffic: { requests: number; average_latency_ms: number; status_groups: Record<string, number> }; external_apis: Record<string, Provider> };

export function MonitoringDashboard() {
  const [data, setData] = useState<Summary | null>(null); const [error, setError] = useState("");
  const load = useCallback(async () => { try { setData(await adminRequest<Summary>("monitoring")); setError(""); } catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao carregar métricas."); } }, []);
  useEffect(() => {
    adminRequest<Summary>("monitoring")
      .then((summary) => setData(summary))
      .catch((reason) => setError(reason instanceof Error ? reason.message : "Falha ao carregar métricas."));
    const timer = window.setInterval(load, 30000);
    return () => window.clearInterval(timer);
  }, [load]);
  const providers = Object.entries(data?.external_apis ?? {});
  return <section className="manager-layout">
    <div className="manager-toolbar"><div><strong><i className="live-dot" /> Métricas em memória</strong><span>atualização automática a cada 30 s</span></div><button className="button secondary" onClick={() => void load()}>Atualizar</button></div>
    {error && <div className="notice error">{error}</div>}
    <div className="monitor-kpis"><article className="card"><span>Requisições</span><strong>{data?.traffic.requests ?? "—"}</strong><small>desde a inicialização</small></article><article className="card"><span>Latência média</span><strong>{data ? `${data.traffic.average_latency_ms} ms` : "—"}</strong><small>todas as rotas</small></article><article className="card"><span>Erros HTTP</span><strong>{data?.traffic.status_groups["5xx"] ?? 0}</strong><small>respostas 5xx</small></article></div>
    <div className="provider-grid">{providers.length === 0 ? <div className="empty-card card">Os provedores aparecerão após a primeira consulta meteorológica.</div> : providers.map(([name, provider]) => <article className="provider-card card" key={name}><div className="provider-head"><span>{name}</span><i className={provider.last_error_code ? "down" : "up"}>{provider.last_error_code ? "atenção" : "operacional"}</i></div><strong>{provider.success_rate_percentage}%</strong><p>taxa de sucesso</p><div className="provider-bar"><i style={{ width: `${provider.success_rate_percentage}%` }} /></div><dl><div><dt>Chamadas</dt><dd>{provider.requests}</dd></div><div><dt>Latência</dt><dd>{provider.average_latency_ms} ms</dd></div><div><dt>Último status</dt><dd>{provider.last_status_code ?? "—"}</dd></div></dl></article>)}</div>
    <div className="monitor-note card"><h2>Escopo atual</h2><p>Estas métricas são locais ao processo FastAPI. Em produção com múltiplas réplicas, exporte-as para OpenTelemetry/Prometheus e centralize logs estruturados.</p></div>
  </section>;
}
