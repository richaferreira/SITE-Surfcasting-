"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import SiteHeader from "../../components/SiteHeader";
import { browserApi } from "../../lib/api";

export default function VerifyEmailPage() {
  const [message, setMessage] = useState("Validando seu e-mail...");
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    const token = new URLSearchParams(window.location.search).get("token");
    if (!token) {
      setMessage("Link de confirmação inválido: token ausente.");
      return;
    }
    browserApi<{ message: string }>("/api/v1/auth/verify-email", {
      method: "POST",
      body: JSON.stringify({ token }),
    })
      .then((response) => {
        setSuccess(true);
        setMessage(response.message);
      })
      .catch((err) => setMessage(err instanceof Error ? err.message : "Não foi possível confirmar o e-mail."));
  }, []);

  return (
    <main>
      <SiteHeader />
      <section className="pageShell authShell">
        <div className="authIntro">
          <span className="eyebrow">Confirmação de conta</span>
          <h1>{success ? "E-mail confirmado." : "Confirmando e-mail."}</h1>
          <p>{message}</p>
          {success ? <Link className="primaryButton" href="/perfil">Ir para meu perfil</Link> : null}
        </div>
      </section>
    </main>
  );
}
