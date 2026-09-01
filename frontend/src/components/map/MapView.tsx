"use client";

import {
  AttributionControl,
  Map as MapLibreMap,
  Marker,
  NavigationControl,
} from "maplibre-gl";
import { useEffect, useRef, useState } from "react";
import { demoPoints } from "@/lib/mock-data";
import type { Beach, FishingPoint } from "@/lib/types";

const layerLabels: Record<FishingPoint["point_type"], string> = {
  BURACO: "Buraco / vala",
  COROA_AREIA: "Coroa de areia",
  CANAL_RETORNO: "Canal de retorno",
  ESTRUTURA: "Estrutura",
  OUTRO: "Outro ponto",
};

const colors: Record<FishingPoint["point_type"], string> = {
  BURACO: "#45d4bd",
  COROA_AREIA: "#f6d365",
  CANAL_RETORNO: "#f18b64",
  ESTRUTURA: "#9fb7ff",
  OUTRO: "#e9f3f5",
};

export function MapView({ beaches, demo: initialDemo }: { beaches: Beach[]; demo: boolean }) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<MapLibreMap | null>(null);
  const markers = useRef<Marker[]>([]);
  const [selectedBeach, setSelectedBeach] = useState(beaches[0]?.slug ?? "");
  const [points, setPoints] = useState<FishingPoint[]>(initialDemo ? demoPoints : []);
  const [activeTypes, setActiveTypes] = useState(() => new Set(Object.keys(layerLabels)));
  const [selectedPoint, setSelectedPoint] = useState<FishingPoint | null>(null);
  const [notice, setNotice] = useState(initialDemo ? "Camadas demonstrativas" : "Dados publicados");
  const beach = beaches.find((item) => item.slug === selectedBeach) ?? beaches[0];

  useEffect(() => {
    if (!container.current || map.current || !beach) return;
    const instance = new MapLibreMap({
      container: container.current,
      center: [beach.longitude, beach.latitude],
      zoom: 11.3,
      attributionControl: false,
      style: {
        version: 8,
        sources: {
          osm: { type: "raster", tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"], tileSize: 256, attribution: "© OpenStreetMap" },
        },
        layers: [{ id: "osm", type: "raster", source: "osm", paint: { "raster-saturation": -0.65, "raster-brightness-max": 0.68, "raster-contrast": 0.2 } }],
      },
    });
    instance.addControl(new NavigationControl({ showCompass: true }), "top-right");
    instance.addControl(new AttributionControl({ compact: true }), "bottom-right");
    map.current = instance;
    return () => { map.current?.remove(); map.current = null; };
  }, [beach]);

  useEffect(() => {
    if (!beach) return;
    let cancelled = false;
    fetch(`/api/public/beaches/${encodeURIComponent(beach.slug)}/points`, { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) throw new Error();
        return (await response.json()) as { items: FishingPoint[] };
      })
      .then((payload) => {
        if (!cancelled) { setPoints(payload.items); setNotice("Dados publicados"); }
      })
      .catch(() => {
        if (!cancelled) { setPoints(demoPoints); setNotice("Camadas demonstrativas"); }
      });
    map.current?.flyTo({ center: [beach.longitude, beach.latitude], zoom: 12, essential: true });
    return () => { cancelled = true; };
  }, [beach]);

  useEffect(() => {
    markers.current.forEach((marker) => marker.remove());
    markers.current = [];
    if (!map.current) return;
    points.filter((point) => activeTypes.has(point.point_type)).forEach((point) => {
      const element = document.createElement("button");
      element.type = "button";
      element.className = "map-marker";
      element.style.setProperty("--marker-color", colors[point.point_type]);
      element.setAttribute("aria-label", `${layerLabels[point.point_type]}: ${point.name}`);
      element.addEventListener("click", () => setSelectedPoint(point));
      markers.current.push(new Marker({ element }).setLngLat([point.longitude, point.latitude]).addTo(map.current!));
    });
  }, [activeTypes, points]);

  function toggleType(type: string) {
    setActiveTypes((current) => {
      const next = new Set(current);
      if (next.has(type)) next.delete(type); else next.add(type);
      return next;
    });
  }

  return (
    <div className="shell map-layout">
      <aside className="map-panel card">
        <label htmlFor="map-beach">Praia</label>
        <select id="map-beach" value={selectedBeach} onChange={(event) => { setSelectedBeach(event.target.value); setSelectedPoint(null); }}>
          {beaches.map((item) => <option key={item.id} value={item.slug}>{item.name}</option>)}
        </select>
        <div className="panel-block">
          <div className="panel-title"><strong>Camadas</strong><span>{points.length} pontos</span></div>
          {Object.entries(layerLabels).map(([type, label]) => (
            <label className="layer-toggle" key={type}>
              <input type="checkbox" checked={activeTypes.has(type)} onChange={() => toggleType(type)} />
              <i style={{ background: colors[type as FishingPoint["point_type"]] }} />{label}
            </label>
          ))}
        </div>
        <div className="map-safety"><strong>Leitura dinâmica</strong><p>Ressacas e marés alteram canais e coroas. Nunca use o mapa como instrução para entrar na água.</p></div>
      </aside>
      <div className="map-canvas-wrap">
        <div className="map-status"><i className="live-dot" />{notice}</div>
        <div ref={container} className="map-canvas" aria-label="Mapa interativo das praias e pontos de pesca" />
        {selectedPoint && (
          <article className="point-sheet card">
            <button type="button" onClick={() => setSelectedPoint(null)} aria-label="Fechar detalhes">×</button>
            <span className="type-label" style={{ color: colors[selectedPoint.point_type] }}>{layerLabels[selectedPoint.point_type]}</span>
            <h2>{selectedPoint.name}</h2>
            <p>{selectedPoint.description}</p>
            <dl><div><dt>Acesso</dt><dd>{selectedPoint.accessibility.toLowerCase()}</dd></div><div><dt>Verificado</dt><dd>{selectedPoint.verified_at ? new Date(selectedPoint.verified_at).toLocaleDateString("pt-BR") : "não informado"}</dd></div></dl>
            {selectedPoint.risk_notes && <div className="notice warning">{selectedPoint.risk_notes}</div>}
          </article>
        )}
      </div>
    </div>
  );
}
