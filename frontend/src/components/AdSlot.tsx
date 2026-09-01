import type { PublicAd } from "@/lib/types";

export function AdSlot({ ads }: { ads: PublicAd[] }) {
  const ad = ads[0];
  if (!ad) return null;
  return (
    <aside className="shell ad-slot" aria-label="Publicidade">
      <span>Publicidade</span>
      <a href={ad.target_url} target="_blank" rel="sponsored nofollow noreferrer">
        <i role="img" aria-label={ad.alt_text} style={{ backgroundImage: `url(${ad.image_url})` }} />
        <strong>{ad.title}</strong>
        <b>Conhecer parceiro ↗</b>
      </a>
    </aside>
  );
}
