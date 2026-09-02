import type { Metadata } from "next";

import SiteHeader from "../../components/SiteHeader";
import { serverApi } from "../../lib/api";

export const metadata: Metadata = {
  title: "Academia",
  description: "Artigos, tutoriais, técnicas e equipamentos para surfcasting na Região dos Lagos.",
};

type Post = {
  id: number;
  author_name: string;
  title: string;
  slug: string;
  excerpt?: string | null;
  content: string;
  content_type: "ARTIGO" | "TUTORIAL" | "VIDEO" | "EQUIPAMENTO";
  featured_image_url?: string | null;
  published_at?: string | null;
  created_at: string;
};

const labels: Record<Post["content_type"], string> = {
  ARTIGO: "Artigo",
  TUTORIAL: "Tutorial",
  VIDEO: "Vídeo",
  EQUIPAMENTO: "Equipamento",
};

export default async function AcademyPage() {
  const posts = (await serverApi<Post[]>("/api/v1/community/posts?limit=100")) ?? [];

  return (
    <main>
      <SiteHeader />
      <section className="pageShell">
        <div className="pageHeading">
          <span className="eyebrow">Academia SRL</span>
          <h1>Conhecimento técnico para evoluir na areia.</h1>
          <p>Conteúdo editorial sobre leitura de praia, arremesso, montagens, equipamentos, segurança e estratégia.</p>
        </div>

        {posts.length ? (
          <div className="cardGrid">
            {posts.map((post) => (
              <article className="panel postCard" key={post.id}>
                {post.featured_image_url ? <img className="academyImage" src={post.featured_image_url} alt="" loading="lazy" /> : null}
                <div className="cardTopline"><span>{labels[post.content_type]}</span><span>{post.author_name}</span></div>
                <h2>{post.title}</h2>
                <p>{post.excerpt ?? post.content.slice(0, 220)}</p>
                <a className="secondaryButton" href={`/academia/${encodeURIComponent(post.slug)}`}>Ler conteúdo</a>
              </article>
            ))}
          </div>
        ) : (
          <div className="notice">A Academia ainda não possui conteúdo publicado. O administrador pode publicar pelo backoffice.</div>
        )}
      </section>
    </main>
  );
}
