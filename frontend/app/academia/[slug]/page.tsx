import type { Metadata } from "next";

import SiteHeader from "../../../components/SiteHeader";
import { serverApi } from "../../../lib/api";

type Post = {
  id: number;
  author_name: string;
  title: string;
  slug: string;
  excerpt?: string | null;
  content: string;
  content_type: string;
  featured_image_url?: string | null;
  video_url?: string | null;
  published_at?: string | null;
  created_at: string;
};

async function loadPost(slug: string): Promise<Post | null> {
  return serverApi<Post>(`/api/v1/community/posts/${encodeURIComponent(slug)}`);
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const post = await loadPost(slug);
  if (!post) return { title: "Conteúdo não encontrado" };
  return {
    title: post.title,
    description: post.excerpt ?? post.content.slice(0, 155),
    openGraph: post.featured_image_url ? { images: [post.featured_image_url] } : undefined,
  };
}

export default async function AcademyPostPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const post = await loadPost(slug);

  if (!post) {
    return <main><SiteHeader /><section className="pageShell"><div className="notice">Conteúdo não encontrado ou ainda não publicado.</div></section></main>;
  }

  const date = new Date(post.published_at ?? post.created_at).toLocaleDateString("pt-BR");

  return (
    <main>
      <SiteHeader />
      <article className="pageShell academyArticle">
        <a className="textButton" href="/academia">← Voltar para a Academia</a>
        <div className="pageHeading">
          <span className="eyebrow">{post.content_type}</span>
          <h1>{post.title}</h1>
          <p>{post.author_name} · {date}</p>
        </div>
        {post.featured_image_url ? <img className="academyHero" src={post.featured_image_url} alt="" /> : null}
        {post.excerpt ? <p className="academyLead">{post.excerpt}</p> : null}
        <div className="panel academyBody">{post.content}</div>
        {post.video_url ? <a className="secondaryButton" href={post.video_url} target="_blank" rel="noreferrer">Abrir vídeo relacionado</a> : null}
      </article>
    </main>
  );
}
