"use client";

import { useEffect, useRef } from "react";

export type BeachMapPoint = {
  id: number;
  name: string;
  point_type: string;
  latitude: number;
  longitude: number;
  accessibility: string;
};

export default function BeachMap({
  beach,
  points,
}: {
  beach: { name: string; latitude: number; longitude: number };
  points: BeachMapPoint[];
}) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    let disposed = false;
    let map: import("leaflet").Map | null = null;

    async function renderMap() {
      const L = await import("leaflet");
      if (disposed || !containerRef.current) return;

      map = L.map(containerRef.current, {
        zoomControl: true,
        scrollWheelZoom: false,
      }).setView([beach.latitude, beach.longitude], 14);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors",
      }).addTo(map);

      const beachPopup = document.createElement("div");
      const beachTitle = document.createElement("strong");
      beachTitle.textContent = beach.name;
      beachPopup.appendChild(beachTitle);
      beachPopup.appendChild(document.createElement("br"));
      beachPopup.appendChild(document.createTextNode("Referência da praia"));

      L.circleMarker([beach.latitude, beach.longitude], {
        radius: 10,
        weight: 3,
        color: "#35d6dd",
        fillColor: "#0b6c73",
        fillOpacity: 0.9,
      }).addTo(map).bindPopup(beachPopup);

      const coordinates: [number, number][] = [[beach.latitude, beach.longitude]];
      for (const point of points) {
        coordinates.push([point.latitude, point.longitude]);
        const popup = document.createElement("div");
        const title = document.createElement("strong");
        title.textContent = point.name;
        popup.appendChild(title);
        popup.appendChild(document.createElement("br"));
        popup.appendChild(document.createTextNode(`${point.point_type.replaceAll("_", " ")} · ${point.accessibility}`));

        L.circleMarker([point.latitude, point.longitude], {
          radius: 8,
          weight: 2,
          color: "#f4c96b",
          fillColor: "#8f6416",
          fillOpacity: 0.9,
        }).addTo(map).bindPopup(popup);
      }

      if (coordinates.length > 1) {
        map.fitBounds(L.latLngBounds(coordinates), { padding: [28, 28], maxZoom: 16 });
      }
    }

    void renderMap();
    return () => {
      disposed = true;
      map?.remove();
    };
  }, [beach.latitude, beach.longitude, beach.name, points]);

  return <div className="beachMap" ref={containerRef} role="region" aria-label={`Mapa de ${beach.name}`} />;
}
