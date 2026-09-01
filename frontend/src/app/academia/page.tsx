import type { Metadata } from "next";
import Link from "next/link";
import { AdSlot } from "@/components/AdSlot";
import { getAcademyPosts, getAds } from "@/lib/api";

export const metadata: Metadata = {
  title: "Academia Long Cast",
  description: "Técnica de arremesso, nós, chicotes, leitura de praia e equipamentos para surfcasting.",
};

const labels = { ARTIGO: "Artigo", TUTORIAL: "Tutorial", VIDEO: "Vídeo", EQUIPAMENTO: "Equipamento" };

export default async function AcademyPage() {
  const [{ items, demo }, ads] = await Promise.all([getAcademyPosts(), getAds("ACADEMIA")]);
  const featured = items[0];
  return (
    <>
      <section className="academy-hero">
        <div className="shell academy-hero-grid">
          <div><span className="eyebrow">Academia Long Cast</span><h1>Mais técnica.<br /><em>Menos improviso.</em></h1><p>Aprendizado direto, fichas precisas e leitura de praia aplicada à Região dos Lagos.</p></div>
          <div className="cast-lines" aria-hidden="true"><i /><i /><i /></div>
        </div>
      </section>
      <section className="shell academy-content">
        {demo && <div className="notice info">Conteúdo demonstrativo ativo enquanto o CMS ainda não possui publicações.</div>}
        {featured && (
          <Link href={`/academia/${featured.slug}`} className="featured-post card">
            <div className="post-art art-tutorial"><span>01</span></div>
            <div><span className="type-label">{labels[featured.content_type]}</span><h2>{featured.title}</h2><p>{featured.excerpt}</p><strong>Ler conteúdo →</strong></div>
          </Link>
        )}
        <div className="section-heading"><div><span className="eyebrow">Biblioteca técnica</span><h2>Continue evoluindo</h2></div><p>{items.length} conteúdos publicados</p></div>
        <div className="post-grid">
          {items.slice(1).map((post, index) => (
            <Link href={`/academia/${post.slug}`} className="post-card card" key={post.id}>
              <div className={`post-art art-${post.content_type.toLowerCase()}`}><span>0{index + 2}</span></div>
              <div><span className="type-label">{labels[post.content_type]}</span><h3>{post.title}</h3><p>{post.excerpt}</p><small>Por {post.author.name}</small></div>
            </Link>
          ))}
        </div>
        <AdSlot ads={ads} />
      </section>
    </>
  );
}
