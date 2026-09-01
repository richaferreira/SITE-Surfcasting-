"use client";

import { FormEvent, useEffect, useState } from "react";

import SiteHeader from "../../components/SiteHeader";
import { browserApi, SessionUser, updateStoredUser } from "../../lib/api";

type Beach = { id: number; name: string; city: string; slug: string };

export default function ProfilePage() {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [beaches, setBeaches] = useState<Beach[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      browserApi<SessionUser>("/api/v1/auth/me", {}, true),
      browserApi<Beach[]>("/api/v1/beaches"),
    ])
      .then(([me, beachList]) => {
        setUser(me);
        updateStoredUser(me);
        setBeaches(beachList);
      })
      .catch((err) => setError(err instanceof Error ? err.message : "Não foi possível carregar o perfil."))
      .finally(() => setLoading(false));
  }, []);

  async function submitProfile(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    const form = new FormData(event.currentTarget);
    try {
      const updated = await browserApi<SessionUser>("/api/v1/auth/me", {
        method: "PATCH",
        body: JSON.stringify({
          name: form.get("name"),
          bio: form.get("bio") || null,
          avatar_url: form.get("avatar_url") || null,
        }),
      }, true);
      setUser(updated);
      updateStoredUser(updated);
      setSuccess("Perfil atualizado.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível atualizar o perfil.");
    }
  }

  async function submitCatch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSuccess(null);
    const form = new FormData(event.currentTarget);
    const praiaId = form.get("praia_id");
    try {
      await browserApi("/api/v1/community/catches", {
        method: "POST",
        body: JSON.stringify({
          praia_id: praiaId ? Number(praiaId) : null,
          species_name: form.get("species_name"),
          bait: form.get("bait") || null,
          technique: form.get("technique") || null,
          weight_kg: form.get("weight_kg") ? Number(form.get("weight_kg")) : null,
          length_cm: form.get("length_cm") ? Number(form.get("length_cm")) : null,
          notes: form.get("notes") || null,
          caught_at: new Date(String(form.get("caught_at"))).toISOString(),
          is_public: true,
        }),
      }, true);
      event.currentTarget.reset();
      setSuccess("Captura registrada e publicada na comunidade.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível registrar a captura.");
    }
  }

  return (
    <main>
      <SiteHeader />
      <section className="pageShell">
        <div className="pageHeading">
          <span className="eyebrow">Perfil do pescador</span>
          <h1>{loading ? "Carregando..." : user?.name ?? "Sua conta"}</h1>
          {user ? <p>@{user.username} · {user.role}</p> : <p>Entre novamente caso sua sessão tenha expirado.</p>}
        </div>

        {error ? <div className="notice errorNotice">{error}</div> : null}
        {success ? <div className="notice successNotice">{success}</div> : null}

        {user ? (
          <div className="twoColumn">
            <article className="panel profileCard">
              <span className="eyebrow">Conta</span>
              <h2>Editar perfil</h2>
              <dl className="detailList">
                <div><dt>Usuário</dt><dd>@{user.username}</dd></div>
                <div><dt>E-mail</dt><dd>{user.email}</dd></div>
                <div><dt>Perfil</dt><dd>{user.role}</dd></div>
              </dl>
              <form className="formStack" onSubmit={submitProfile}>
                <label>Nome<input name="name" defaultValue={user.name} required minLength={2} /></label>
                <label>Avatar (URL)<input name="avatar_url" type="url" defaultValue={user.avatar_url ?? ""} /></label>
                <label>Bio<textarea name="bio" rows={4} maxLength={500} defaultValue={user.bio ?? ""} /></label>
                <button className="primaryButton formButton" type="submit">Salvar perfil</button>
              </form>
              {user.role === "ADMIN" ? <a className="secondaryButton profileAdminLink" href="/admin">Abrir backoffice</a> : null}
            </article>

            <article className="panel">
              <span className="eyebrow">Diário de pesca</span>
              <h2>Registrar captura</h2>
              <form className="formStack" onSubmit={submitCatch}>
                <label>
                  Praia
                  <select name="praia_id" defaultValue="">
                    <option value="">Não informar</option>
                    {beaches.map((beach) => <option key={beach.id} value={beach.id}>{beach.name} · {beach.city}</option>)}
                  </select>
                </label>
                <label>Espécie<input name="species_name" required minLength={2} /></label>
                <div className="formGrid">
                  <label>Isca<input name="bait" /></label>
                  <label>Técnica<input name="technique" /></label>
                  <label>Peso (kg)<input name="weight_kg" type="number" min="0" step="0.001" /></label>
                  <label>Comprimento (cm)<input name="length_cm" type="number" min="0" step="0.1" /></label>
                </div>
                <label>Data e hora<input name="caught_at" type="datetime-local" required /></label>
                <label>Observações<textarea name="notes" rows={4} maxLength={1000} /></label>
                <button className="primaryButton formButton" type="submit">Publicar captura</button>
              </form>
            </article>
          </div>
        ) : null}
      </section>
    </main>
  );
}
