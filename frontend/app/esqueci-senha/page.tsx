"use client";

import { FormEvent, useState } from "react";

import SiteHeader from "../../components/SiteHeader";
import { browserApi } from "../../lib/api";

export default function ForgotPasswordPage() {
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setMessage(null);
    const form = new FormData(event.currentTarget);
    try {
      const response = await browserApi<{ message: string }>("/api/v1/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email: form.get("email") }),
      });
      setMessage(response.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Não foi possível solicitar a redefinição.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main>
      <SiteHeader />
      <section className="pageShell authShell">
        <div className="authIntro">
          <span className="eyebrow">Recuperação de conta</span>
          <h1>Redefina sua senha com segurança.</h1>
          <p>Informe o e-mail cadastrado. Se a conta existir, enviaremos um link válido por 30 minutos.</p>
        </div>
        <article className="panel authCard">
          {message ? <div className="notice successNotice">{message}</div> : null}
          {error ? <div className="notice errorNotice">{error}</div> : null}
          <form className="formStack" onSubmit={submit}>
            <label>E-mail<input name="email" type="email" autoComplete="email" required /></label>
            <button className="primaryButton formButton" disabled={loading} type="submit">
              {loading ? "Enviando..." : "Enviar link de recuperação"}
            </button>
          </form>
        </article>
      </section>
    </main>
  );
}
