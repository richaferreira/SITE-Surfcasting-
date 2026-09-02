import CommunityActions from "../../components/CommunityActions";
import SiteHeader from "../../components/SiteHeader";
import { serverApi } from "../../lib/api";

type Post = {
  id: number;
  author_name: string;
  title: string;
  slug: string;
  excerpt?: string | null;
  content: string;
  content_type: string;
  published_at?: string | null;
  created_at: string;
  likes: number;
  comments: number;
};

type Catch = {
  id: number;
  user_name: string;
  beach_name?: string | null;
  species_name: string;
  bait?: string | null;
  technique?: string | null;
  weight_kg?: number | null;
  length_cm?: number | null;
  notes?: string | null;
  caught_at: string;
};

export default async function CommunityPage() {
  const [posts, catches] = await Promise.all([
    serverApi<Post[]>("/api/v1/community/posts?limit=20"),
    serverApi<Catch[]>("/api/v1/community/catches?limit=30"),
  ]);

  return (
    <main>
      <SiteHeader />
      <section className="pageShell">
        <div className="pageHeading communityHeading">
          <div>
            <span className="eyebrow">Comunidade SRL</span>
            <h1>Conhecimento que vem da areia.</h1>
            <p>Relatos de captura, conteúdo técnico e experiências compartilhadas por pescadores da Região dos Lagos.</p>
          </div>
          <a className="primaryButton" href="/perfil">Registrar captura</a>
        </div>

        <div className="communityLayout">
          <div className="feedColumn">
            <h2>Conteúdo técnico</h2>
            {posts?.length ? posts.map((post) => (
              <article className="panel postCard" key={post.id}>
                <div className="cardTopline"><span>{post.content_type}</span><span>{post.author_name}</span></div>
                <h2>{post.title}</h2>
                <p>{post.excerpt ?? post.content.slice(0, 260)}</p>
                <small>{new Date(post.published_at ?? post.created_at).toLocaleDateString("pt-BR")}</small>
                <CommunityActions postId={post.id} initialLikes={post.likes} initialComments={post.comments} />
              </article>
            )) : <div className="notice">Ainda não há artigos publicados.</div>}
          </div>

          <aside className="catchColumn">
            <h2>Capturas recentes</h2>
            {catches?.length ? catches.map((item) => (
              <article className="panel catchCard" key={item.id}>
                <div className="cardTopline"><span>{item.user_name}</span><span>{new Date(item.caught_at).toLocaleDateString("pt-BR")}</span></div>
                <h3>{item.species_name}</h3>
                <p>{item.beach_name ?? "Local não informado"}</p>
                <div className="catchStats">
                  {item.weight_kg != null ? <span>{item.weight_kg.toFixed(2)} kg</span> : null}
                  {item.length_cm != null ? <span>{item.length_cm.toFixed(1)} cm</span> : null}
                  {item.bait ? <span>Isca: {item.bait}</span> : null}
                </div>
                {item.notes ? <small>{item.notes}</small> : null}
              </article>
            )) : <div className="notice">Nenhuma captura pública foi registrada ainda.</div>}
          </aside>
        </div>
      </section>
    </main>
  );
}
