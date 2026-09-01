import SiteHeader from "../../../components/SiteHeader";
import { serverApi } from "../../../lib/api";

type Point = {
  id: number;
  name: string;
  point_type: string;
  description?: string | null;
  latitude: number;
  longitude: number;
  accessibility: string;
  access_notes?: string | null;
  risk_notes?: string | null;
};

type Beach = {
  id: number;
  name: string;
  slug: string;
  city: string;
  state: string;
  description?: string | null;
  latitude: number;
  longitude: number;
  sea_bearing_deg: number;
  beach_profile: string;
  accessibility_summary?: string | null;
  points: Point[];
};

type Score = {
  score: number;
  label: string;
  calculated_at: string;
  conditions: {
    wind_speed_mps: number | null;
    wind_direction_deg: number | null;
    wind_is_offshore: boolean | null;
    tide_trend: string;
    wave_height_m: number | null;
    wave_period_s: number | null;
    water_temperature_c: number | null;
    pressure_hpa: number | null;
    moon_phase: string;
  };
  reasons: string[];
  warnings: string[];
};

type RecommendationPayload = {
  recommendations: { species: string; relevance: number }[];
  explanation: string;
};

function value(value: number | null, suffix: string, digits = 1) {
  return value === null ? "--" : `${value.toFixed(digits)}${suffix}`;
}

export default async function BeachPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const beach = await serverApi<Beach>(`/api/v1/beaches/${encodeURIComponent(slug)}`);

  if (!beach) {
    return (
      <main><SiteHeader /><section className="pageShell"><div className="notice">Praia não encontrada ou ainda não publicada.</div></section></main>
    );
  }

  const scoreParams = new URLSearchParams({
    latitude: String(beach.latitude),
    longitude: String(beach.longitude),
    sea_bearing_deg: String(beach.sea_bearing_deg),
  });
  const score = await serverApi<Score>(`/api/v1/fishing-score?${scoreParams.toString()}`);

  let recommendation: RecommendationPayload | null = null;
  if (
    score &&
    score.conditions.wind_direction_deg !== null &&
    score.conditions.wind_speed_mps !== null &&
    score.conditions.water_temperature_c !== null
  ) {
    const tide = score.conditions.tide_trend.toUpperCase().includes("FALL") ? "FALLING" : "RISING";
    const recParams = new URLSearchParams({
      wind_direction_deg: String(score.conditions.wind_direction_deg),
      wind_speed_mps: String(score.conditions.wind_speed_mps),
      water_temperature_c: String(score.conditions.water_temperature_c),
      tide_key: tide,
    });
    recommendation = await serverApi<RecommendationPayload>(`/api/v1/recommendations/${encodeURIComponent(slug)}?${recParams.toString()}`);
  }

  const c = score?.conditions;

  return (
    <main>
      <SiteHeader />
      <section className="pageShell">
        <div className="pageHeading beachHeroHeading">
          <div>
            <span className="eyebrow">{beach.city} · {beach.state}</span>
            <h1>{beach.name}</h1>
            <p>{beach.description ?? beach.accessibility_summary ?? "Leitura técnica desta praia."}</p>
          </div>
          <div className="scoreMini">
            <strong>{score?.score ?? "--"}</strong><span>/100</span>
            <small>{score?.label ?? "Telemetria indisponível"}</small>
          </div>
        </div>

        <div className="metricGrid pageMetrics">
          <article className="metricCard"><span>Vento</span><strong>{value(c?.wind_speed_mps ?? null, " m/s")}</strong><small>{c?.wind_is_offshore == null ? "--" : c.wind_is_offshore ? "Terral" : "Maral"}</small></article>
          <article className="metricCard"><span>Ondas</span><strong>{value(c?.wave_height_m ?? null, " m")}</strong><small>Período {value(c?.wave_period_s ?? null, " s")}</small></article>
          <article className="metricCard"><span>Água</span><strong>{value(c?.water_temperature_c ?? null, " °C")}</strong><small>Pressão {value(c?.pressure_hpa ?? null, " hPa", 0)}</small></article>
          <article className="metricCard"><span>Maré</span><strong>{c?.tide_trend?.replaceAll("_", " ") ?? "--"}</strong><small>Lua {c?.moon_phase ?? "--"}</small></article>
        </div>

        <div className="twoColumn">
          <article className="panel">
            <span className="eyebrow">Pontos cadastrados</span>
            <h2>Leitura da praia</h2>
            {beach.points.length ? (
              <div className="stackList">
                {beach.points.map((point) => (
                  <div className="listItem" key={point.id}>
                    <div><strong>{point.name}</strong><span>{point.point_type.replaceAll("_", " ")} · {point.accessibility}</span></div>
                    <p>{point.description ?? point.access_notes ?? "Sem observações adicionais."}</p>
                    {point.risk_notes ? <small className="riskText">Atenção: {point.risk_notes}</small> : null}
                  </div>
                ))}
              </div>
            ) : <p className="muted">Nenhum ponto específico foi cadastrado ainda.</p>}
          </article>

          <article className="panel">
            <span className="eyebrow">Neo4j</span>
            <h2>Espécies favorecidas</h2>
            {recommendation?.recommendations.length ? (
              <div className="stackList">
                {recommendation.recommendations.map((item) => (
                  <div className="listItem compactItem" key={item.species}>
                    <strong>{item.species}</strong><span>Relevância {item.relevance.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            ) : <p className="muted">Ainda não há uma combinação cadastrada no grafo para as condições atuais.</p>}
            <small>{recommendation?.explanation ?? "A recomendação aparece quando há telemetria suficiente e relações cadastradas no grafo."}</small>
          </article>
        </div>
      </section>
    </main>
  );
}
