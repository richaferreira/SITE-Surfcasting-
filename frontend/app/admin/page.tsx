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

export default function AdminPage() {
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const load = useCallback(async () => {
    try {
      const [stats, userList] = await Promise.all([
        browserApi<Dashboard>("/api/v1/admin/dashboard", {}, true),
        browserApi<AdminUser[]>("/api/v1/admin/users", {}, true),
      ]);
      setDashboard(stats);
      setUsers(userList);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível abrir o backoffice.");
    }
  }, []);

  useEffect(() => { void load(); }, [load]);

  async function changeRole(userId: number, role: AdminUser["role"]) {
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
          description: form.get("description") || null,
          latitude: Number(form.get("latitude")),
          longitude: Number(form.get("longitude")),
          sea_bearing_deg: Number(form.get("sea_bearing_deg")),
          beach_profile: form.get("beach_profile"),
          accessibility_summary: form.get("accessibility_summary") || null,
          is_published: true,
        }),
      }, true);
      event.currentTarget.reset();
      setSuccess("Praia cadastrada e publicada.");
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
          excerpt: form.get("excerpt") || null,
          content: form.get("content"),
          content_type: form.get("content_type"),
          featured_image_url: null,
          video_url: null,
        }),
      }, true);
      event.currentTarget.reset();
      setSuccess("Conteúdo criado e publicado.");
      await load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível publicar o conteúdo.");
    }
  }

  const metrics = dashboard ? [
    ["Usuários", dashboard.users], ["Ativos", dashboard.active_users],
    ["Praias", dashboard.published_beaches], ["Posts", dashboard.published_posts],
    ["Capturas", dashboard.catches], ["Comentários", dashboard.comments],
  ] : [];

  return (
    <main>
      <SiteHeader />
      <section className="pageShell adminShell">
        <div className="pageHeading"><span className="eyebrow">Backoffice</span><h1>Central administrativa</h1><p>Gestão de usuários, praias e conteúdo com ações auditáveis.</p></div>
        {error ? <div className="notice errorNotice">{error}</div> : null}
        {success ? <div className="notice successNotice">{success}</div> : null}

        <div className="adminMetrics">
          {metrics.map(([label, number]) => <article className="metricCard" key={String(label)}><span>{label}</span><strong>{number}</strong></article>)}
        </div>

        <div className="twoColumn adminForms">
          <article className="panel">
            <span className="eyebrow">CMS geográfico</span><h2>Nova praia</h2>
            <form className="formStack" onSubmit={createBeach}>
              <div className="formGrid"><label>Nome<input name="name" required /></label><label>Slug<input name="slug" required pattern="[a-z0-9-]+" /></label><label>Cidade<input name="city" required /></label><label>UF<input name="state" defaultValue="RJ" maxLength={2} required /></label></div>
              <label>Descrição<textarea name="description" rows={3} /></label>
              <div className="formGrid"><label>Latitude<input name="latitude" type="number" step="0.000001" required /></label><label>Longitude<input name="longitude" type="number" step="0.000001" required /></label><label>Direção para o mar (°)<input name="sea_bearing_deg" type="number" min="0" max="359.99" step="0.01" required /></label><label>Perfil<select name="beach_profile" defaultValue="INTERMEDIARIA"><option value="TOMBO">Tombo</option><option value="INTERMEDIARIA">Intermediária</option><option value="RASA">Rasa</option><option value="ABRIGADA">Abrigada</option></select></label></div>
              <label>Acesso<input name="accessibility_summary" /></label>
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
              <label>Conteúdo<textarea name="content" rows={8} minLength={20} required /></label>
              <button className="primaryButton formButton" type="submit">Publicar</button>
            </form>
          </article>
        </div>

        <article className="panel tablePanel">
          <div className="panelHeading"><div><span className="eyebrow">Acessos</span><h2>Usuários</h2></div><span>{users.length} carregados</span></div>
          <div className="tableWrap">
            <table><thead><tr><th>Usuário</th><th>E-mail</th><th>Perfil</th><th>Status</th></tr></thead><tbody>
              {users.map((user) => <tr key={user.id}><td><strong>{user.name}</strong><small>@{user.username}</small></td><td>{user.email}</td><td><select value={user.role} onChange={(event) => void changeRole(user.id, event.target.value as AdminUser["role"])}><option value="USER">Usuário</option><option value="AUTHOR">Autor</option><option value="ADMIN">Admin</option></select></td><td><button className="textButton" onClick={() => void toggleUser(user)} type="button">{user.is_active ? "Ativo" : "Inativo"}</button></td></tr>)}
            </tbody></table>
          </div>
        </article>
      </section>
    </main>
  );
}
