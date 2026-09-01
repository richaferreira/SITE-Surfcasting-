import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "Surfcasting Região dos Lagos",
    short_name: "Surfcasting RL",
    description: "Condições do mar, mapa técnico e Academia Long Cast.",
    start_url: "/",
    display: "standalone",
    background_color: "#071d26",
    theme_color: "#071d26",
    lang: "pt-BR",
    orientation: "portrait-primary",
    categories: ["sports", "weather", "education"],
    icons: [
      { src: "/icons/icon-192.svg", sizes: "192x192", type: "image/svg+xml", purpose: "any" },
      { src: "/icons/icon-512.svg", sizes: "512x512", type: "image/svg+xml", purpose: "maskable" },
    ],
  };
}
