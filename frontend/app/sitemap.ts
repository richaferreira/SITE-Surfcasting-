import type { MetadataRoute } from "next";

import { serverApi } from "../lib/api";

type Beach = { slug: string };
type Post = { slug: string; published_at?: string | null; created_at: string };

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const base = (process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000").replace(/\/$/, "");
  const [beaches, posts] = await Promise.all([
    serverApi<Beach[]>("/api/v1/beaches"),
    serverApi<Post[]>("/api/v1/community/posts?limit=100"),
  ]);
  const staticRoutes = ["", "/praias", "/academia", "/comunidade", "/termos", "/privacidade"];

  return [
    ...staticRoutes.map((path) => ({
      url: `${base}${path}`,
      lastModified: new Date(),
      changeFrequency: path === "" ? "hourly" as const : "daily" as const,
      priority: path === "" ? 1 : 0.8,
    })),
    ...(beaches ?? []).map((beach) => ({
      url: `${base}/praias/${beach.slug}`,
      lastModified: new Date(),
      changeFrequency: "hourly" as const,
      priority: 0.9,
    })),
    ...(posts ?? []).map((post) => ({
      url: `${base}/academia/${post.slug}`,
      lastModified: new Date(post.published_at ?? post.created_at),
      changeFrequency: "weekly" as const,
      priority: 0.75,
    })),
  ];
}
