import type { CSSProperties } from "react";

import SiteHeader from "../components/SiteHeader";

type Conditions = {
  wind_speed_mps: number | null;
  wind_direction_deg: number | null;
  sea_bearing_deg: number;
  wind_is_offshore: boolean | null;
  tide_trend: string;
  wave_height_m: number | null;
  wave_period_s: number | null;
  water_temperature_c: number | null;
  pressure_hpa: number | null;
  moon_phase: string;
};

type FishingScore = {
  score: number;
  label: string;
  calculated_at: string;
  conditions: Conditions;
  breakdown: Record<string, number>;
  reasons: string[];
  warnings: string[];
};

const DEFAULT_SPOT = {
  name: "Praia de Itaúna",
  city: "Saquarema - RJ",
  latitude: -22.935,
  longitude: -42.483,
  seaBearing: 160,
};

const API_URL = process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function formatNumber(value: number | null, suffix: string, digits = 1) {
  return value === null ? "--" : `${value.toFixed(digits)}${suffix}`;
}

function scoreTone(score: number) {
  if (score >= 80) return "Excelente";
  if (score >= 65) return "Muito bom";
  if (score >= 50) return "Razoável";
  return "Atenção";
}

async function getFishingScore(): Promise<{ data: FishingScore | null; error: string | null }> {
  const params = new URLSearchParams({
    latitude: String(DEFAULT_SPOT.latitude),
    longitude: String(DEFAULT_SPOT.longitude),
    sea_bearing_deg: String(DEFAULT_SPOT.seaBearing),
  });
  try {
    const response = await fetch(`${API_URL}/api/v1/fishing-score?${params.toString()}`, { next: { revalidate: 300 } });
    if (!response.ok) return { data: null, error: "A telemetria ainda não está disponível. Verifique as chaves das APIs no backend." };
    return { data: (await response.json()) as FishingScore, error: null };
  } catch {
    return { data: null, error: "Não foi possível conectar à API. Confirme se o backend está em execução." };
  }
}

export default async function Home() {
  const { data, error } = await getFishingScore();
  const conditions = data?.conditions;
  const score = data?.score ?? 0;
  const metrics = [
    { label: "Vento", value: formatNumber(conditions?.wind_speed_mps ?? null, " m/s"), detail: conditions?.wind_is_offshore == null ? "Direção indisponível" : conditions.wind_is_offshore ? "Terral • favorável" : "Maral • observar" },
    { label: "Ondas", value: formatNumber(conditions?.wave_height_m ?? null, " m"), detail: `Período ${formatNumber(conditions?.wave_period_s ?? null, " s")}` },
    { label: "Maré", value: conditions?.tide_trend ? conditions.tide_trend.replaceAll("_", " ") : "--", detail: "Tendência atual" },
    { label: "Água", value: formatNumber(conditions?.water_temperature_c ?? null, " °C"), detail: `Pressão ${formatNumber(conditions?.pressure_hpa ?? null, " hPa", 0)}` },
  ];

  return (
    <main>
      <SiteHeader />
      <section className="hero" id="inicio">
        <div className="heroGlow" aria-hidden="true" />
        <div className="heroContent">
          <span className="eyebrow">Leitura inteligente da costa</span>
          <h1>Saiba quando a praia está chamando.</h1>
          <p>Vento, maré, ondas, temperatura, pressão e conhecimento local em uma plataforma para planejar a próxima pescaria na Região dos Lagos.</p>
          <div className="heroActions"><a className="primaryButton" href="#score">Ver condições agora</a><a className="secondaryButton" href="/praias">Explorar praias</a></div>
        </div>
        <div className="heroRadar" aria-hidden="true">
          <div className="radarRing ringOne" /><div className="radarRing ringTwo" /><div className="radarRing ringThree" /><div className="radarSweep" /><div className="radarDot dotOne" /><div className="radarDot dotTwo" /><div className="radarCenter">🎣</div>
        </div>
      </section>

      <section className="dashboard" id="condicoes">
        <div className="sectionHeading"><div><span className="eyebrow">Agora em destaque</span><h2>{DEFAULT_SPOT.name}</h2><p>{DEFAULT_SPOT.city}</p></div><span className="liveBadge"><i /> telemetria</span></div>
        {error ? <div className="notice">{error}</div> : null}
        <div className="metricGrid">{metrics.map((metric) => <article className="metricCard" key={metric.label}><span>{metric.label}</span><strong>{metric.value}</strong><small>{metric.detail}</small></article>)}</div>
      </section>

      <section className="scoreSection" id="score">
        <article className="scoreCard">
          <div className="scoreGauge" style={{ "--score": `${score * 3.6}deg` } as CSSProperties}><div><strong>{data ? data.score : "--"}</strong><span>/100</span></div></div>
          <div className="scoreCopy"><span className="eyebrow">Score de Pesca</span><h2>{data ? `${scoreTone(data.score)} para pescar` : "Aguardando dados"}</h2><p>{data?.label ?? "Assim que as integrações meteorológicas estiverem configuradas, o score aparecerá aqui."}</p>{data?.calculated_at ? <small>Atualizado em {new Date(data.calculated_at).toLocaleString("pt-BR")}</small> : null}</div>
        </article>
        <article className="analysisCard">
          <div className="analysisHeader"><div><span className="eyebrow">Por que esse resultado?</span><h3>Leitura explicável</h3></div><span className="moon">☾ {conditions?.moon_phase ?? "--"}</span></div>
          <div className="breakdownList">{data && Object.keys(data.breakdown).length ? Object.entries(data.breakdown).map(([name, value]) => <div className="breakdownItem" key={name}><div><span>{name.replaceAll("_", " ")}</span><strong>{Math.round(value)} pts</strong></div><div className="progressTrack"><span style={{ width: `${Math.min(100, Math.max(0, value * 3.33))}%` }} /></div></div>) : <p className="muted">Os componentes do score serão exibidos quando houver telemetria.</p>}</div>
        </article>
      </section>

      <section className="featureSection">
        <div className="sectionHeading"><div><span className="eyebrow">Portal completo</span><h2>Da previsão à comunidade.</h2></div></div>
        <div className="featureGrid">
          <a href="/praias"><article><span className="featureIcon">⌖</span><h3>Praias e pontos</h3><p>Mapeamento de praias, canais, buracos, coroas, acessos e leitura de risco.</p></article></a>
          <a href="/praias/praia-de-itauna"><article><span className="featureIcon">◎</span><h3>Recomendação inteligente</h3><p>Relações Neo4j entre condição ambiental, praia e espécie-alvo.</p></article></a>
          <a href="/comunidade"><article><span className="featureIcon">♧</span><h3>Comunidade local</h3><p>Capturas, comentários, curtidas e conteúdo técnico construído por quem pesca na região.</p></article></a>
        </div>
      </section>

      <footer><div className="brand footerBrand"><span className="brandMark">SRL</span><span><strong>Surfcasting</strong><small>Região dos Lagos</small></span></div><p>Informação para planejar melhor. Segurança e leitura da praia sempre vêm primeiro.</p></footer>
    </main>
  );
}
