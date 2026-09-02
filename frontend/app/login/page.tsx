"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import SiteHeader from "../../components/SiteHeader";
import { AuthPayload, browserApi, saveSession } from "../../lib/api";

export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submitLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    const form = new FormData(event.currentTarget);
    try {
      const payload = await browserApi<AuthPayload>("/api/v1/auth/login", {
        method: "POST",
        body: JSON.stringify({ login: form.get("login"), password: form.get("password") }),
      });
      saveSession(payload);
      window.location.href = payload.user.role === "ADMIN" ? "/admin" : "/perfil";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível entrar.");
    } finally {
      setLoading(false);
    }
  }

  async function submitRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    const form = new FormData(event.currentTarget);
    try {
      const payload = await browserApi<AuthPayload>("/api/v1/auth/register", {
        method: "POST",
        body: JSON.stringify({
          name: form.get("name"),
          username: form.get("username"),
          email: form.get("email"),
          password: form.get("password"),
          accept_terms: form.get("accept_terms") === "on",
          accept_privacy: form.get("accept_privacy") === "on",
        }),
      });
      saveSession(payload);
      window.location.href = "/perfil?confirmar-email=1";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível criar sua conta.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <SiteHeader />
      <section className="pageShell authShell">
        <div className="authIntro">
          <span className="eyebrow">Sua conta SRL</span>
          <h1>Pesque com informação e compartilhe experiência.</h1>
          <p>Salve praias, publique capturas e participe da comunidade local usando uma conta única.</p>
        </div>

        <article className="panel authCard">
          <div className="tabRow">
            <button className={mode === "login" ? "tabActive" : ""} onClick={() => setMode("login")} type="button">Entrar</button>
            <button className={mode === "register" ? "tabActive" : ""} onClick={() => setMode("register")} type="button">Criar conta</button>
          </div>

          {error ? <div className="notice errorNotice">{error}</div> : null}

          {mode === "login" ? (
            <form className="formStack" onSubmit={submitLogin}>
              <label>
                E-mail ou usuário
                <input name="login" autoComplete="username" required minLength={3} />
              </label>
              <label>
                Senha
                <input name="password" type="password" autoComplete="current-password" required minLength={8} />
              </label>
              <div className="formMetaRow">
                <Link href="/esqueci-senha">Esqueci minha senha</Link>
              </div>
              <button className="primaryButton formButton" disabled={loading} type="submit">
                {loading ? "Entrando..." : "Entrar"}
              </button>
            </form>
          ) : (
            <form className="formStack" onSubmit={submitRegister}>
              <label>
                Nome
                <input name="name" autoComplete="name" required minLength={2} />
              </label>
              <label>
                Usuário
                <input name="username" autoComplete="username" required minLength={3} pattern="[A-Za-z0-9_.-]+" />
              </label>
              <label>
                E-mail
                <input name="email" type="email" autoComplete="email" required />
              </label>
              <label>
                Senha
                <input name="password" type="password" autoComplete="new-password" required minLength={8} />
              </label>
              <label className="consentRow">
                <input name="accept_terms" type="checkbox" required />
                <span>Li e aceito os <Link href="/termos" target="_blank">Termos de Uso</Link>.</span>
              </label>
              <label className="consentRow">
                <input name="accept_privacy" type="checkbox" required />
                <span>Li a <Link href="/privacidade" target="_blank">Política de Privacidade</Link> e concordo com o tratamento descrito.</span>
              </label>
              <button className="primaryButton formButton" disabled={loading} type="submit">
                {loading ? "Criando..." : "Criar conta"}
              </button>
            </form>
          )}
        </article>
      </section>
    </main>
  );
}
