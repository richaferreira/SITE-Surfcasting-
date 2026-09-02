"use client";

import { useEffect, useState } from "react";

import SiteHeader from "../../../components/SiteHeader";
import { browserApi } from "../../../lib/api";

type Report = {
  id: number;
  reporter_id: number;
  post_id: number | null;
  comment_id: number | null;
  reason: string;
  details: string | null;
  status: "ABERTO" | "EM_ANALISE" | "RESOLVIDO" | "DESCARTADO";
  created_at: string;
};

type Monitoring = {
  dependencies: { status: string; dependencies: Record<string, string> };
  runtime: {
    requests_total: number;
    errors_total: number;
    error_rate: number;
    average_latency_ms: number;
    providers: Record<string, { requests: number; errors: number; average_latency_ms: number }>;
  };
  database: Record<string, number>;
};

type Analytics = {
  total_events: number;
  unique_sessions: number;
  top_pages: Array<{ page: string; events: number }>;
  top_beaches: Array<{ beach: string; events: number }>;
  top_events: Array<{ event: string; events: number }>;
};

export default function OperationsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [monitoring, setMonitoring] = useState<Monitoring | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [error, setError] = useState<string | null>(null);

  function load() {
    setError(null);
    Promise.all([
      browserApi<Report[]>("/api/v1/admin/reports?limit=100", {}, true),
      browserApi<Monitoring>("/api/v1/admin/monitoring", {}, true),
      browserApi<Analytics>("/api/v1/admin/analytics/summary?days=30", {}, true),
    ])
      .then(([reportItems, monitoringData, analyticsData]) => {
        setReports(reportItems);
        setMonitoring(monitoringData);
        setAnalytics(analyticsData);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Não foi possível carregar a operação."));
  }

  useEffect(load, []);

  async function updateReport(id: number, status: Report["status"]) {
    const updated = await browserApi<Report>(`/api/v1/admin/reports/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }, true);
    setReports((current) => current.map((item) => item.id === id ? updated : item));
  }

  return (
    <main>
      <SiteHeader />
      <section className="pageShell">
        <div className="pageHeading actionHeading">
          <div>
            <span className="eyebrow">Backoffice · Operação</span>
            <h1>Saúde, uso e moderação</h1>
            <p>Visão operacional da API, provedores, banco, audiência e denúncias.</p>
          </div>
          <a className="secondaryButton" href="/admin">Voltar ao painel</a>
        </div>

        {error ? <div className="notice errorNotice">{error}</div> : null}

        {monitoring ? (
          <div className="adminMetricGrid">
            <article className="panel"><span className="eyebrow">Readiness</span><h2>{monitoring.dependencies.status}</h2><p>MySQL: {monitoring.dependencies.dependencies.mysql} · Neo4j: {monitoring.dependencies.dependencies.neo4j}</p></article>
            <article className="panel"><span className="eyebrow">Tráfego</span><h2>{monitoring.runtime.requests_total}</h2><p>{monitoring.runtime.average_latency_ms} ms de latência média</p></article>
            <article className="panel"><span className="eyebrow">Erros 5xx</span><h2>{monitoring.runtime.errors_total}</h2><p>{(monitoring.runtime.error_rate * 100).toFixed(2)}% das requisições</p></article>
            <article className="panel"><span className="eyebrow">Denúncias abertas</span><h2>{monitoring.database.open_reports ?? 0}</h2><p>{monitoring.database.analytics_events_24h ?? 0} eventos de analytics nas últimas 24h</p></article>
          </div>
        ) : null}

        {analytics ? (
          <div className="twoColumn adminOperationsGrid">
            <article className="panel">
              <span className="eyebrow">Analytics · 30 dias</span>
              <h2>{analytics.unique_sessions} sessões · {analytics.total_events} eventos</h2>
              <h3>Páginas mais acessadas</h3>
              <ul className="dataList">{analytics.top_pages.map((item) => <li key={item.page}><span>{item.page}</span><strong>{item.events}</strong></li>)}</ul>
            </article>
            <article className="panel">
              <span className="eyebrow">Praias</span>
              <h2>Interesse por destino</h2>
              <ul className="dataList">{analytics.top_beaches.length ? analytics.top_beaches.map((item) => <li key={item.beach}><span>{item.beach}</span><strong>{item.events}</strong></li>) : <li>Nenhum dado ainda.</li>}</ul>
            </article>
          </div>
        ) : null}

        <article className="panel operationReports">
          <div className="actionHeading">
            <div><span className="eyebrow">Moderação</span><h2>Denúncias da comunidade</h2></div>
            <button className="textButton" type="button" onClick={load}>Atualizar</button>
          </div>
          <div className="reportAdminList">
            {reports.length === 0 ? <p>Nenhuma denúncia registrada.</p> : reports.map((report) => (
              <div className="reportAdminRow" key={report.id}>
                <div>
                  <strong>#{report.id} · {report.reason}</strong>
                  <p>{report.details || "Sem detalhes adicionais."}</p>
                  <small>{report.post_id ? `Publicação #${report.post_id}` : `Comentário #${report.comment_id}`} · {new Date(report.created_at).toLocaleString("pt-BR")}</small>
                </div>
                <select value={report.status} onChange={(event) => void updateReport(report.id, event.target.value as Report["status"])}>
                  <option value="ABERTO">Aberto</option>
                  <option value="EM_ANALISE">Em análise</option>
                  <option value="RESOLVIDO">Resolvido</option>
                  <option value="DESCARTADO">Descartado</option>
                </select>
              </div>
            ))}
          </div>
        </article>
      </section>
    </main>
  );
}
