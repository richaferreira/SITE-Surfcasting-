"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { ConditionsChart } from "./ConditionsChart";
import { ScoreRing } from "./ScoreRing";
import { demoScore } from "@/lib/mock-data";
import type { Beach, FishingScore, MarineForecast } from "@/lib/types";

type Props = { beaches: Beach[]; initialDemo: boolean };

const conditionMeta = [
  ["wave_height_m", "Altura do swell", "m"],
  ["wave_period_s", "Período", "s"],
  ["wind_speed_mps", "Vento", "m/s"],
  ["water_temperature_c", "Água", "°C"],
  ["pressure_hpa", "Pressão", "hPa"],
] as const;

function tideName(type: "high" | "low") {
  return type === "high" ? "preamar" : "baixa-mar";
}

export function DashboardClient({ beaches, initialDemo }: Props) {
  const [selectedSlug, setSelectedSlug] = useState(beaches[0]?.slug ?? "");
  const [score, setScore] = useState<FishingScore>(demoScore);
  const [forecast, setForecast] = useState<MarineForecast | null>(null);
  const [demo, setDemo] = useState(initialDemo);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const beach = beaches.find((item) => item.slug === selectedSlug) ?? beaches[0];

  function selectBeach(slug: string) {
    setSelectedSlug(slug);
    setScore(demoScore);
    setForecast(null);
    setDemo(true);
    setMessage("Praia alterada. Atualize para carregar a telemetria desta localização.");
  }

  async function refreshScore() {
    if (!beach) return;
    setLoading(true);
    setMessage("");
    try {
      const scoreQuery = new URLSearchParams({
        latitude: String(beach.latitude),
        longitude: String(beach.longitude),
        sea_bearing_deg: String(beach.sea_bearing_deg),
      });
      const forecastQuery = new URLSearchParams({
        latitude: String(beach.latitude),
        longitude: String(beach.longitude),
        hours: "24",
      });
      const [scoreResponse, forecastResponse] = await Promise.all([
        fetch(`/api/public/fishing-score?${scoreQuery}`, { cache: "no-store" }),
        fetch(`/api/public/forecast?${forecastQuery}`, { cache: "no-store" }),
      ]);

      const scorePayload = await scoreResponse.json();
      if (!scoreResponse.ok) {
        throw new Error(scorePayload.detail ?? "Não foi possível atualizar o score.");
      }

      setScore(scorePayload as FishingScore);
      setDemo(false);

      if (forecastResponse.ok) {
        const forecastPayload = (await forecastResponse.json()) as MarineForecast;
        setForecast(forecastPayload);
        setMessage("Condições e previsão horária atualizadas.");
      } else {
        setForecast(null);
        setMessage("Condições atualizadas; a série horária está temporariamente indisponível.");
      }
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Falha temporária ao atualizar.");
    } finally {
      setLoading(false);
    }
  }

  const chartData = useMemo(() => {
    if (!forecast) return [];
    const points: Array<{ time: string; onda: number; vento: number }> = [];
    forecast.hours.forEach((item, index) => {
      if (index % 3 !== 0 || item.wave_height_m === null || item.wind_speed_mps === null) return;
      points.push({
        time: new Date(item.observed_at).toLocaleTimeString("pt-BR", {
          hour: "2-digit",
          minute: "2-digit",
        }),
        onda: item.wave_height_m,
        vento: item.wind_speed_mps,
      });
    });
    return points.slice(0, 8);
  }, [forecast]);

  const nextTide = useMemo(() => forecast?.tides[0] ?? null, [forecast]);

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
            <select id="beach" value={selectedSlug} onChange={(event) => selectBeach(event.target.value)}>
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
            {nextTide ? (
              <p>
                Próxima {tideName(nextTide.extreme_type)} às {new Date(nextTide.occurs_at).toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}
                {nextTide.height_m === null ? "." : ` · ${nextTide.height_m.toFixed(2)} m.`}
              </p>
            ) : (
              <p>Atualize para carregar os próximos extremos de maré retornados pelo provedor.</p>
            )}
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
            <div><span className="eyebrow">Tendência real</span><h2>Próximas 24 horas</h2></div>
            <div className="chart-legend"><span className="wave-key">Onda (m)</span><span className="wind-key">Vento (m/s)</span></div>
          </div>
          {chartData.length >= 2 ? (
            <ConditionsChart data={chartData} />
          ) : (
            <div className="notice" role="note">Atualize as condições para carregar uma série horária real. Nenhuma curva é estimada localmente.</div>
          )}
          <p className="chart-note">
            {forecast
              ? `Fonte ${forecast.source}. Cobertura ${forecast.data_quality.coverage_percentage}% (${forecast.data_quality.hours_returned}/${forecast.data_quality.hours_requested} horas retornadas).`
              : "A tendência só é desenhada quando o provedor devolve dados horários suficientes."}
          </p>
          {forecast?.warnings[0] && <div className="notice warning" role="note">{forecast.warnings[0]}</div>}
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
