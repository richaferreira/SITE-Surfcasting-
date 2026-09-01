"use client";

import type { Route } from "next";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, useState } from "react";

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const data = new FormData(event.currentTarget);
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username: data.get("username"), password: data.get("password") }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail ?? "Não foi possível entrar.");
      const next = searchParams.get("next");
      router.push((next?.startsWith("/admin") ? next : "/admin") as Route);
      router.refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Falha temporária.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="login-card card" onSubmit={submit}>
      <div><span className="eyebrow">Acesso seguro</span><h2>Entre na sua conta</h2><p>Use seu nome de usuário e senha.</p></div>
      <label>Usuário<input name="username" autoComplete="username" required minLength={3} /></label>
      <label>Senha<input name="password" type="password" autoComplete="current-password" required minLength={8} /></label>
      {error && <div className="notice error" role="alert">{error}</div>}
      <button className="button primary full" type="submit" disabled={loading}>{loading ? "Entrando…" : "Entrar na conta"}</button>
      <p className="form-alternative">Ainda não participa? <Link href="/cadastro">Criar conta</Link></p>
      <small>O token permanece em cookie HttpOnly e não fica exposto ao JavaScript do navegador.</small>
    </form>
  );
}
