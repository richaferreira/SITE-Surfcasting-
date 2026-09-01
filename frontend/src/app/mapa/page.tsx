import type { Metadata } from "next";
import { MapShell } from "@/components/map/MapShell";
import { AdSlot } from "@/components/AdSlot";
import { getAds, getBeaches } from "@/lib/api";

export const metadata: Metadata = {
  title: "Mapa técnico de pesca",
  description: "Mapa de buracos, coroas de areia, canais de retorno e acessibilidade nas praias da Região dos Lagos.",
};

export default async function MapPage() {
  const [{ items, demo }, ads] = await Promise.all([getBeaches(), getAds("MAPA")]);
  return (
    <section className="map-page">
      <div className="shell map-heading">
        <div><span className="eyebrow">Inteligência geográfica</span><h1>Encontre a estrutura.<br /><em>Leia o movimento.</em></h1></div>
        <p>Referências verificadas de pesca e acesso. O fundo muda: confirme cada estrutura visualmente antes de pescar.</p>
      </div>
      <MapShell beaches={items} demo={demo} />
      <AdSlot ads={ads} />
    </section>
  );
}
