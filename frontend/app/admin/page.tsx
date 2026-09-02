"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";

import SiteHeader from "../../components/SiteHeader";
import { browserApi } from "../../lib/api";

type Dashboard = {
  users: number;
  active_users: number;
  beaches: number;
  published_beaches: number;
  posts: number;
  published_posts: number;
  catches: number;
  comments: number;
};

type AdminUser = {
  id: number;
  name: string;
  username: string;
  email: string;
  role: "ADMIN" | "AUTHOR" | "USER";
  is_active: boolean;
};

type AdminBeach = {
  id: number;
  name: string;
  slug: string;
  city: string;
  state: string;
  latitude: number;
  longitude: number;
  sea_bearing_deg: number;
  beach_profile: string;
  is_published: boolean;
};

type AdminPost = {
  id: number;
  author_id: number;
  author_name: string;
  title: string;
  slug: string;
  excerpt: string | null;
  content: string;
  content_type: "ARTIGO" | "TUTORIAL" | "VIDEO" | "EQUIPAMENTO";
  status: "RASCUNHO" | "EM_REVISAO" | "PUBLICADO" | "ARQUIVADO";
  featured_image_url: string | null;
  video_url: string | null;
  published_at: string | null;
  created_at: string;
  updated_at: string;
};

type AdminComment = {
  id: number;
  post_id: number;
  post_title: string;
  author_id: number;
  author_name: string;
  content: string;
  status: "PUBLICADO" | "OCULTO" | "REMOVIDO";
  created_at: string;
};

function optionalText(form: FormData, key: string) {
  const value = String(form.get(key) ?? "").trim();
  return value || null;
}

export default function AdminPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [beaches, setBeaches] = useState<AdminBeach[]>([]);
  const [posts, setPosts] = useState<AdminPost[]>([]);
  const [comments, setComments] = useState<AdminComment[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const [stats, userList, beachList, postList, commentList] = await Promise.all([
        browserApi<Dashboard>("/api/v1/admin/dashboard", {}, true),
        browserApi<AdminUser[]>("/api/v1/admin/users", {}, true),
        browserApi<AdminBeach[]>("/api/v1/beaches/manage", {}, true),
        browserApi<AdminPost[]>("/api/v1/admin/posts", {}, true),
        browserApi<AdminComment[]>("/api/v1/admin/comments", {}, true),
      ]);
      setDashboard(stats);
      setUsers(userList);
      setBeaches(beachList);
      setPosts(postList);
      setComments(commentList);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível abrir o backoffice.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  async function changeRole(userId: number, role: AdminUser["role"]) {
    setError(null);
    try {
      const updated = await browserApi<AdminUser>(`/api/v1/admin/users/${userId}/role`, {
        method: "PATCH",
        body: JSON.stringify({ role }),
      }, true);
      setUsers((items) => items.map((item) => item.id === userId ? updated : item));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível alterar o perfil.");
    }
  }

  async function toggleUser(user: AdminUser) {
    setError(null);
    try {
      const updated = await browserApi<AdminUser>(`/api/v1/admin/users/${user.id}/active`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !user.is_active }),
      }, true);
      setUsers((items) => items.map((item) => item.id === user.id ? updated : item));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível alterar o usuário.");
    }
  }

  async function createBeach(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null); setSuccess(null);
    const form = new FormData(event.currentTarget);
    try {
      await browserApi("/api/v1/beaches", {
        method: "POST",
        body: JSON.stringify({
          name: form.get("name"),
          slug: form.get("slug"),
          city: form.get("city"),
          state: form.get("state"),
          description: optionalText(form, "description"),
          latitude: Number(form.get("latitude")),
          longitude: Number(form.get("longitude")),
          sea_bearing_deg: Number(form.get("sea_bearing_deg")),
          beach_profile: form.get("beach_profile"),
          accessibility_summary: optionalText(form, "accessibility_summary"),
          is_published: form.get("is_published") === "on",
        }),
      }, true);
      event.currentTarget.reset();
      setSuccess("Praia cadastrada.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível cadastrar a praia.");
    }
  }

  async function createPost(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null); setSuccess(null);
    const form = new FormData(event.currentTarget);
    try {
      await browserApi("/api/v1/community/posts", {
        method: "POST",
        body: JSON.stringify({
          title: form.get("title"),
          slug: form.get("slug"),
          excerpt: optionalText(form, "excerpt"),
          content: form.get("content"),
          content_type: form.get("content_type"),
          featured_image_url: optionalText(form, "featured_image_url"),
          video_url: optionalText(form, "video_url"),
        }),
      }, true);
      event.currentTarget.reset();
      setSuccess("Conteúdo criado e publicado.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível publicar o conteúdo.");
    }
  }

  async function updatePost(event: FormEvent<HTMLFormElement>, postId: number) {
    event.preventDefault();
    setError(null); setSuccess(null);
    const form = new FormData(event.currentTarget);
    try {
      await browserApi(`/api/v1/admin/posts/${postId}`, {
        method: "PATCH",
        body: JSON.stringify({
          title: form.get("title"),
          slug: form.get("slug"),
          excerpt: optionalText(form, "excerpt"),
          content: form.get("content"),
          content_type: form.get("content_type"),
          featured_image_url: optionalText(form, "featured_image_url"),
          video_url: optionalText(form, "video_url"),
        }),
      }, true);
      setSuccess("Publicação atualizada.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível editar a publicação.");
    }
  }

  async function changePostStatus(postId: number, status: AdminPost["status"]) {
    setError(null); setSuccess(null);
    try {
      await browserApi(`/api/v1/admin/posts/${postId}/status`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      }, true);
      setPosts((items) => items.map((item) => item.id === postId ? { ...item, status } : item));
      setSuccess("Status da publicação atualizado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível alterar o status.");
    }
  }

  async function deletePost(post: AdminPost) {
    if (!window.confirm(`Excluir definitivamente “${post.title}”?`)) return;
    setError(null); setSuccess(null);
    try {
      await browserApi(`/api/v1/admin/posts/${post.id}`, { method: "DELETE" }, true);
      setPosts((items) => items.filter((item) => item.id !== post.id));
      setSuccess("Publicação excluída.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível excluir a publicação.");
    }
  }

  async function toggleComment(comment: AdminComment) {
    setError(null); setSuccess(null);
    try {
      if (comment.status === "PUBLICADO") {
        await browserApi(`/api/v1/admin/comments/${comment.id}`, { method: "DELETE" }, true);
      } else {
        await browserApi(`/api/v1/admin/comments/${comment.id}/restore`, { method: "POST" }, true);
      }
      await load();
      setSuccess(comment.status === "PUBLICADO" ? "Comentário ocultado." : "Comentário restaurado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível moderar o comentário.");
    }
  }

  const metrics = dashboard ? [
    ["Usuários", dashboard.users], ["Ativos", dashboard.active_users],
    ["Praias", `${dashboard.published_beaches}/${dashboard.beaches}`],
    ["Posts", `${dashboard.published_posts}/${dashboard.posts}`],
    ["Capturas", dashboard.catches], ["Comentários", dashboard.comments],
  ] : [];

  return (
    <main>
      <SiteHeader />
      <section className="pageShell adminShell">
        <div className="pageHeading">
          <span className="eyebrow">Backoffice</span>
          <h1>Central administrativa</h1>
          <p>Gestão de usuários, praias, spots, conteúdo e moderação em um único painel.</p>
        </div>
        {error ? <div className="notice errorNotice">{error}</div> : null}
        {success ? <div className="notice successNotice">{success}</div> : null}
        {loading ? <div className="notice">Carregando dados administrativos...</div> : null}

        <div className="adminMetrics">
          {metrics.map(([label, number]) => <article className="metricCard" key={String(label)}><span>{label}</span><strong>{number}</strong></article>)}
        </div>

        <article className="panel adminBeachManager">
          <div className="panelHeading">
            <div><span className="eyebrow">CMS geográfico</span><h2>Praias cadastradas</h2></div>
            <span>{beaches.length} registro(s)</span>
          </div>
          <div className="adminBeachGrid">
            {beaches.map((beach) => (
              <a className="adminBeachCard" href={`/admin/praias/${encodeURIComponent(beach.slug)}`} key={beach.id}>
                <div><strong>{beach.name}</strong><span>{beach.city} · {beach.state}</span></div>
                <small>{beach.beach_profile.replaceAll("_", " ")} · {beach.is_published ? "publicada" : "rascunho"}</small>
                <b>Editar praia e spots →</b>
              </a>
            ))}
            {!beaches.length && !loading ? <p className="muted">Nenhuma praia cadastrada.</p> : null}
          </div>
        </article>

        <div className="twoColumn adminForms">
          <article className="panel">
            <span className="eyebrow">CMS geográfico</span><h2>Nova praia</h2>
            <form className="formStack" onSubmit={createBeach}>
              <div className="formGrid"><label>Nome<input name="name" required /></label><label>Slug<input name="slug" required pattern="[a-z0-9-]+" /></label><label>Cidade<input name="city" required /></label><label>UF<input name="state" defaultValue="RJ" maxLength={2} required /></label></div>
              <label>Descrição<textarea name="description" rows={3} /></label>
              <div className="formGrid"><label>Latitude<input name="latitude" type="number" step="0.000001" required /></label><label>Longitude<input name="longitude" type="number" step="0.000001" required /></label><label>Direção para o mar (°)<input name="sea_bearing_deg" type="number" min="0" max="359.99" step="0.01" required /></label><label>Perfil<select name="beach_profile" defaultValue="INTERMEDIARIA"><option value="TOMBO">Tombo</option><option value="INTERMEDIARIA">Intermediária</option><option value="RASA">Rasa</option><option value="ABRIGADA">Abrigada</option></select></label></div>
              <label>Acesso<input name="accessibility_summary" /></label>
              <label className="checkboxLabel"><input name="is_published" type="checkbox" defaultChecked /> Publicar imediatamente</label>
              <button className="primaryButton formButton" type="submit">Cadastrar praia</button>
            </form>
          </article>

          <article className="panel">
            <span className="eyebrow">Conteúdo</span><h2>Nova publicação</h2>
            <form className="formStack" onSubmit={createPost}>
              <label>Título<input name="title" required minLength={4} /></label>
              <label>Slug<input name="slug" required pattern="[a-z0-9-]+" /></label>
              <label>Tipo<select name="content_type" defaultValue="ARTIGO"><option value="ARTIGO">Artigo</option><option value="TUTORIAL">Tutorial</option><option value="EQUIPAMENTO">Equipamento</option><option value="VIDEO">Vídeo</option></select></label>
              <label>Resumo<textarea name="excerpt" rows={2} maxLength={500} /></label>
              <label>Imagem de destaque (URL)<input name="featured_image_url" type="url" /></label>
              <label>Vídeo (URL)<input name="video_url" type="url" /></label>
              <label>Conteúdo<textarea name="content" rows={8} minLength={20} required /></label>
              <button className="primaryButton formButton" type="submit">Publicar</button>
            </form>
          </article>
        </div>

        <article className="panel adminContentPanel">
          <div className="panelHeading"><div><span className="eyebrow">Conteúdo</span><h2>Publicações</h2></div><span>{posts.length} registro(s)</span></div>
          <div className="contentEditorList">
            {posts.map((post) => (
              <details className="contentEditor" key={post.id}>
                <summary>
                  <span><strong>{post.title}</strong><small>{post.author_name} · {post.content_type} · {post.status}</small></span>
                  <span>Editar</span>
                </summary>
                <div className="contentStatusRow">
                  <label>Status<select value={post.status} onChange={(event) => void changePostStatus(post.id, event.target.value as AdminPost["status"])}><option value="RASCUNHO">Rascunho</option><option value="EM_REVISAO">Em revisão</option><option value="PUBLICADO">Publicado</option><option value="ARQUIVADO">Arquivado</option></select></label>
                  <button className="dangerButton" type="button" onClick={() => void deletePost(post)}>Excluir publicação</button>
                </div>
                <form className="formStack" onSubmit={(event) => void updatePost(event, post.id)}>
                  <div className="formGrid"><label>Título<input name="title" defaultValue={post.title} required /></label><label>Slug<input name="slug" defaultValue={post.slug} required pattern="[a-z0-9-]+" /></label></div>
                  <label>Tipo<select name="content_type" defaultValue={post.content_type}><option value="ARTIGO">Artigo</option><option value="TUTORIAL">Tutorial</option><option value="EQUIPAMENTO">Equipamento</option><option value="VIDEO">Vídeo</option></select></label>
                  <label>Resumo<textarea name="excerpt" rows={2} defaultValue={post.excerpt ?? ""} /></label>
                  <div className="formGrid"><label>Imagem de destaque<input name="featured_image_url" type="url" defaultValue={post.featured_image_url ?? ""} /></label><label>Vídeo<input name="video_url" type="url" defaultValue={post.video_url ?? ""} /></label></div>
                  <label>Conteúdo<textarea name="content" rows={8} minLength={20} defaultValue={post.content} required /></label>
                  <button className="primaryButton formButton" type="submit">Salvar publicação</button>
                </form>
              </details>
            ))}
            {!posts.length && !loading ? <p className="muted">Nenhuma publicação cadastrada.</p> : null}
          </div>
        </article>

        <div className="twoColumn adminModerationColumns">
          <article className="panel tablePanel">
            <div className="panelHeading"><div><span className="eyebrow">Acessos</span><h2>Usuários</h2></div><span>{users.length} carregados</span></div>
            <div className="tableWrap">
              <table><thead><tr><th>Usuário</th><th>E-mail</th><th>Perfil</th><th>Status</th></tr></thead><tbody>
                {users.map((user) => <tr key={user.id}><td><strong>{user.name}</strong><small>@{user.username}</small></td><td>{user.email}</td><td><select value={user.role} onChange={(event) => void changeRole(user.id, event.target.value as AdminUser["role"])}><option value="USER">Usuário</option><option value="AUTHOR">Autor</option><option value="ADMIN">Admin</option></select></td><td><button className="textButton" onClick={() => void toggleUser(user)} type="button">{user.is_active ? "Ativo" : "Inativo"}</button></td></tr>)}
              </tbody></table>
            </div>
          </article>

          <article className="panel moderationPanel">
            <div className="panelHeading"><div><span className="eyebrow">Moderação</span><h2>Comentários</h2></div><span>{comments.length} recentes</span></div>
            <div className="moderationList">
              {comments.map((comment) => (
                <div className="moderationItem" key={comment.id}>
                  <div><strong>{comment.author_name}</strong><span>{comment.status}</span></div>
                  <small>Em: {comment.post_title}</small>
                  <p>{comment.content}</p>
                  <button className="secondaryButton moderationButton" type="button" onClick={() => void toggleComment(comment)}>{comment.status === "PUBLICADO" ? "Ocultar" : "Restaurar"}</button>
                </div>
              ))}
              {!comments.length && !loading ? <p className="muted">Nenhum comentário para moderar.</p> : null}
            </div>
          </article>
        </div>
      </section>
    </main>
  );
}
