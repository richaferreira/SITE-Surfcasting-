"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ConditionsChart } from "./ConditionsChart";
import { ScoreRing } from "./ScoreRing";
import { demoScore } from "@/lib/mock-data";
import type { Beach, FishingScore } from "@/lib/types";

type Props = { beaches: Beach[]; initialDemo: boolean };

const conditionMeta = [
  ["wave_height_m", "Altura do swell", "m"],
  ["wave_period_s", "Período", "s"],
  ["wind_speed_mps", "Vento", "m/s"],
  ["water_temperature_c", "Água", "°C"],
  ["pressure_hpa", "Pressão", "hPa"],
] as const;

export function DashboardClient({ beaches, initialDemo }: Props) {
  const [selectedSlug, setSelectedSlug] = useState(beaches[0]?.slug ?? "");
  const [score, setScore] = useState<FishingScore>(demoScore);
  const [demo, setDemo] = useState(initialDemo);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const beach = beaches.find((item) => item.slug === selectedSlug) ?? beaches[0];

  async function refreshScore() {
    if (!beach) return;
    setLoading(true);
    setMessage("");
    try {
      const query = new URLSearchParams({
        latitude: String(beach.latitude),
        longitude: String(beach.longitude),
        sea_bearing_deg: String(beach.sea_bearing_deg),
      });
      const response = await fetch(`/api/public/fishing-score?${query}`, { cache: "no-store" });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "Não foi possível atualizar o score.");
      setScore(payload as FishingScore);
      setDemo(false);
      setMessage("Condições atualizadas.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha temporária ao atualizar.");
    } finally {
      setLoading(false);
    }
  }

  const chartData = useMemo(() => {
    const wave = score.conditions.wave_height_m ?? 0;
    const wind = score.conditions.wind_speed_mps ?? 0;
    return Array.from({ length: 8 }, (_, index) => ({
      time: `${String((new Date().getHours() + index * 3) % 24).padStart(2, "0")}h`,
      onda: Number(Math.max(0, wave + Math.sin(index * 0.8) * 0.18).toFixed(1)),
      vento: Number(Math.max(0, wind + Math.cos(index * 0.7) * 1.1).toFixed(1)),
    }));
  }, [score]);

  return (
    <>
      <section className="hero dashboard-hero">
        <div className="shell hero-grid">
          <div>
            <span className="eyebrow"><i className="live-dot" /> Condições para a próxima janela</span>
            <h1>Leia o mar.<br /><em>Escolha melhor.</em></h1>
            <p>Telemetria oceanográfica traduzida em uma decisão clara para o seu próximo arremesso.</p>
          </div>
          <div className="beach-control card">
            <label htmlFor="beach">Praia monitorada</label>
            <select id="beach" value={selectedSlug} onChange={(event) => setSelectedSlug(event.target.value)}>
              {beaches.map((item) => <option key={item.id} value={item.slug}>{item.name} · {item.city}</option>)}
            </select>
            <div className="control-row">
              <span>{beach?.beach_profile.toLowerCase()} · mar a {beach?.sea_bearing_deg}°</span>
              <button className="text-button" type="button" onClick={refreshScore} disabled={loading}>
                {loading ? "Atualizando…" : "Atualizar agora"}
              </button>
            </div>
            {message && <p className="form-message" role="status">{message}</p>}
          </div>
        </div>
      </section>

      <section className="shell dashboard-section" aria-labelledby="score-title">
        <div className="score-layout">
          <article className="score-card card">
            <div className="section-heading compact">
              <div><span className="eyebrow">Score de pesca</span><h2 id="score-title">Janela atual</h2></div>
              <span className={`source-pill ${demo ? "demo" : "live"}`}>{demo ? "Demonstração" : score.cached ? "Cache recente" : "Ao vivo"}</span>
            </div>
            <div className="score-main">
              <ScoreRing value={score.score} label={score.label} />
              <div className="score-copy">
                <h3>{score.score === null ? "Aguarde dados essenciais" : "Condições promissoras"}</h3>
                <p>{score.reasons[0] ?? "Cruze as condições com a leitura visual da praia."}</p>
                <ul className="reason-list">
                  {score.reasons.slice(1, 4).map((reason) => <li key={reason}>{reason}</li>)}
                </ul>
                <div className="confidence">
                  <span>Confiança dos dados</span><strong>{score.data_quality.confidence_percentage}%</strong>
                  <div><i style={{ width: `${score.data_quality.confidence_percentage}%` }} /></div>
                </div>
              </div>
            </div>
            {score.warnings.length > 0 && <div className="notice warning" role="note">{score.warnings[0]}</div>}
          </article>

          <aside className="next-tide card">
            <span className="eyebrow">Maré</span>
            <strong>{score.conditions.tide_trend}</strong>
            <p>O algoritmo favorece a enchente, mas estruturas locais podem mudar a melhor janela.</p>
            <div className="tide-line" aria-hidden="true"><i /><i /><i /><i /></div>
            <Link href="/mapa">Cruzar com o mapa técnico →</Link>
          </aside>
        </div>

        <div className="condition-grid" aria-label="Condições oceanográficas">
          {conditionMeta.map(([key, label, unit]) => {
            const value = score.conditions[key];
            return (
              <article className="metric-card card" key={key}>
                <span>{label}</span>
                <strong>{value ?? "—"}<small>{value === null ? "" : unit}</small></strong>
                <p>{key === "wind_speed_mps" && score.conditions.wind_is_offshore ? "Terral" : key === "wave_period_s" ? "Energia moderada" : "Leitura atual"}</p>
              </article>
            );
          })}
        </div>

        <article className="chart-card card">
          <div className="section-heading compact">
            <div><span className="eyebrow">Tendência</span><h2>Próximas 21 horas</h2></div>
            <div className="chart-legend"><span className="wave-key">Onda (m)</span><span className="wind-key">Vento (m/s)</span></div>
          </div>
          <ConditionsChart data={chartData} />
          <p className="chart-note">A curva é estimada a partir da leitura atual até que o provedor forneça uma série horária completa.</p>
        </article>
      </section>

      <section className="cta-band">
        <div className="shell cta-grid">
          <div><span className="eyebrow">Antes de sair</span><h2>Veja onde a praia está trabalhando.</h2><p>Buracos, coroas, canais de retorno, acesso e alertas em uma só leitura.</p></div>
          <Link className="button primary" href="/mapa">Abrir mapa técnico</Link>
        </div>
      </section>
    </>
  );
}
