"use client";

import Link from "next/link";
import { FormEvent, useEffect, useState } from "react";

import SiteHeader from "../../components/SiteHeader";
import { browserApi } from "../../lib/api";

export default function ResetPasswordPage() {
  const [token, setToken] = useState("");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setToken(new URLSearchParams(window.location.search).get("token") ?? "");
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    const form = new FormData(event.currentTarget);
    const password = String(form.get("password") ?? "");
    const confirmation = String(form.get("confirmation") ?? "");
    if (password !== confirmation) {
      setError("As senhas informadas não são iguais.");
      setLoading(false);
      return;
    }
    if (!token) {
      setError("O link de redefinição não contém um token válido.");
      setLoading(false);
      return;
    }
    try {
      const response = await browserApi<{ message: string }>("/api/v1/auth/reset-password", {
        method: "POST",
        body: JSON.stringify({ token, new_password: password }),
      });
      setMessage(response.message);
      event.currentTarget.reset();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível redefinir a senha.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <SiteHeader />
      <section className="pageShell authShell">
        <div className="authIntro">
          <span className="eyebrow">Nova senha</span>
          <h1>Proteja novamente sua conta.</h1>
          <p>Depois da alteração, todas as sessões anteriores são revogadas automaticamente.</p>
        </div>
        <article className="panel authCard">
          {message ? <div className="notice successNotice">{message} <Link href="/login">Entrar</Link></div> : null}
          {error ? <div className="notice errorNotice">{error}</div> : null}
          <form className="formStack" onSubmit={submit}>
            <label>Nova senha<input name="password" type="password" minLength={8} autoComplete="new-password" required /></label>
            <label>Confirmar senha<input name="confirmation" type="password" minLength={8} autoComplete="new-password" required /></label>
            <button className="primaryButton formButton" disabled={loading || !token} type="submit">
              {loading ? "Salvando..." : "Redefinir senha"}
            </button>
          </form>
        </article>
      </section>
    </main>
  );
}
