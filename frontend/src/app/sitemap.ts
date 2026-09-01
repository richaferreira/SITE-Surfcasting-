import type { MetadataRoute } from "next";
import { getAcademyPosts } from "@/lib/api";

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";
  const { items } = await getAcademyPosts();
  return [
    { url: siteUrl, changeFrequency: "hourly", priority: 1 },
    { url: `${siteUrl}/mapa`, changeFrequency: "daily", priority: 0.8 },
    { url: `${siteUrl}/academia`, changeFrequency: "weekly", priority: 0.8 },
    { url: `${siteUrl}/comunidade`, changeFrequency: "daily", priority: 0.7 },
    ...items.map((post) => ({
      url: `${siteUrl}/academia/${post.slug}`,
      lastModified: post.published_at ? new Date(post.published_at) : undefined,
      changeFrequency: "monthly" as const,
      priority: 0.7,
    })),
  ];
}
