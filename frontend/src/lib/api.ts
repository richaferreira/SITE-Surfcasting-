import { demoBeaches, demoPostDetails, demoPosts, demoThreads } from "./mock-data";
import type { AcademyPost, AcademyPostSummary, Beach, CommunityThread, PublicAd } from "./types";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000/api/v1";

async function apiGet<T>(path: string, revalidate = 300): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      next: { revalidate },
      signal: AbortSignal.timeout(4500),
      headers: { Accept: "application/json" },
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export async function getBeaches(): Promise<{ items: Beach[]; demo: boolean }> {
  const data = await apiGet<{ items: Beach[] }>("/beaches?limit=100", 300);
  if (!data?.items.length) return { items: demoBeaches, demo: true };
  return { items: data.items, demo: false };
}

export async function getAcademyPosts(): Promise<{
  items: AcademyPostSummary[];
  demo: boolean;
}> {
  const data = await apiGet<{ items: AcademyPostSummary[] }>("/academy/posts?limit=50", 300);
  if (!data?.items.length) return { items: demoPosts, demo: true };
  return { items: data.items, demo: false };
}

export async function getAcademyPost(slug: string): Promise<{ item: AcademyPost | null; demo: boolean }> {
  const data = await apiGet<AcademyPost>(`/academy/posts/${encodeURIComponent(slug)}`, 300);
  if (data) return { item: data, demo: false };
  return { item: demoPostDetails[slug] ?? null, demo: true };
}

export async function getCommunityThreads(): Promise<{ items: CommunityThread[]; demo: boolean }> {
  const data = await apiGet<{ items: CommunityThread[] }>("/community/threads?limit=50", 60);
  if (!data?.items.length) return { items: demoThreads, demo: true };
  return { items: data.items, demo: false };
}

export async function getCommunityThread(id: number): Promise<{ item: CommunityThread | null; demo: boolean }> {
  const data = await apiGet<CommunityThread>(`/community/threads/${id}`, 30);
  if (data) return { item: data, demo: false };
  return { item: demoThreads.find((thread) => thread.id === id) ?? null, demo: true };
}

export async function getAds(placement: PublicAd["placement"]): Promise<PublicAd[]> {
  const data = await apiGet<{ items: PublicAd[] }>(`/ads?placement=${placement}`, 60);
  return data?.items ?? [];
}

export { API_BASE_URL };
