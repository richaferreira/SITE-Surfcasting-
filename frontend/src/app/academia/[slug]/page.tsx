import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { getAcademyPost } from "@/lib/api";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const { item } = await getAcademyPost(slug);
  if (!item) return { title: "Conteúdo não encontrado" };
  return { title: item.seo_title ?? item.title, description: item.seo_description ?? item.excerpt };
}

export default async function PostPage({ params }: Props) {
  const { slug } = await params;
  const { item: post, demo } = await getAcademyPost(slug);
  if (!post) notFound();
  const specs = post.equipment_specification;
  return (
    <article className="article-page">
      <header className="article-header"><div className="shell article-shell"><Link href="/academia">← Academia Long Cast</Link><span className="type-label">{post.content_type.toLowerCase()}</span><h1>{post.title}</h1><p>{post.excerpt}</p><div className="article-meta"><span>Por {post.author.name}</span><span>{post.published_at ? new Date(post.published_at).toLocaleDateString("pt-BR") : "Em revisão"}</span>{demo && <span>Demonstração</span>}</div></div></header>
      <div className="shell article-shell article-body">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{post.content}</ReactMarkdown>
        {specs && (
          <section className="spec-card card" aria-labelledby="spec-title">
            <span className="eyebrow">Ficha técnica</span><h2 id="spec-title">Configuração do conjunto</h2>
            <dl>
              <div><dt>Vara</dt><dd>{specs.rod_length_m} m · {specs.rod_construction}</dd></div>
              <div><dt>Molinete</dt><dd>Tamanho {specs.reel_size}</dd></div>
              <div><dt>Linha principal</dt><dd>{specs.main_line_material} {specs.main_line_diameter_mm} mm</dd></div>
              <div><dt>Shock leader</dt><dd>{specs.shock_leader_type}</dd></div>
              <div><dt>Peso de arremesso</dt><dd>{specs.casting_weight_min_g}–{specs.casting_weight_max_g} g</dd></div>
            </dl>
          </section>
        )}
        <div className="article-safety"><strong>Segurança no arremesso</strong><p>Inspecione linha, shock leader e nó. Mantenha a área de giro livre e respeite a capacidade indicada pela vara.</p></div>
      </div>
    </article>
  );
}
