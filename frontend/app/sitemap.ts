import type { MetadataRoute } from "next";

import { serverApi } from "../lib/api";

type Beach = { slug: string };

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = (process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000").replace(/\/$/, "");
  const beaches = (await serverApi<Beach[]>("/api/v1/beaches")) ?? [];
  const staticRoutes = ["", "/praias", "/comunidade", "/termos", "/privacidade"];

  return [
    ...staticRoutes.map((path) => ({
      url: `${base}${path}`,
      lastModified: new Date(),
      changeFrequency: path === "" ? "hourly" as const : "daily" as const,
      priority: path === "" ? 1 : 0.8,
    })),
    ...beaches.map((beach) => ({
      url: `${base}/praias/${beach.slug}`,
      lastModified: new Date(),
      changeFrequency: "hourly" as const,
      priority: 0.9,
    })),
  ];
}
