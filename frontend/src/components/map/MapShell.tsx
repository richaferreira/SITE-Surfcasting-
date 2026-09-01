"use client";

import dynamic from "next/dynamic";
import type { Beach } from "@/lib/types";

const MapView = dynamic(() => import("./MapView").then((module) => module.MapView), {
  ssr: false,
  loading: () => <div className="map-loading" role="status">Carregando mapa técnico…</div>,
});

export function MapShell({ beaches, demo }: { beaches: Beach[]; demo: boolean }) {
  return <MapView beaches={beaches} demo={demo} />;
}
