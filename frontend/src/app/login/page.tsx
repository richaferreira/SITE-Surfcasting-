import type { Metadata } from "next";
import { Suspense } from "react";
import { LoginForm } from "@/components/LoginForm";

export const metadata: Metadata = { title: "Entrar", robots: { index: false, follow: false } };

export default function LoginPage() {
  return (
    <section className="login-page">
      <div className="shell login-grid">
        <div className="login-intro">
          <span className="eyebrow">Sua conta</span>
          <h1>Conhecimento local fica melhor quando é compartilhado.</h1>
          <p>Participe da comunidade. Autores e administradores também acessam suas ferramentas editoriais.</p>
          <div className="login-wave" aria-hidden="true" />
        </div>
        <Suspense fallback={<div className="login-card card">Carregando acesso…</div>}><LoginForm /></Suspense>
      </div>
    </section>
  );
}
