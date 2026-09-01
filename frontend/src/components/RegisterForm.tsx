"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

export function RegisterForm() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoading(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const payload = {
      name: form.get("name"),
      username: form.get("username"),
      email: form.get("email"),
      password: form.get("password"),
    };
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        const detail = Array.isArray(data.detail)
          ? data.detail.map((item: { msg?: string }) => item.msg).join("; ")
          : data.detail;
        throw new Error(detail ?? "Não foi possível criar a conta.");
      }
      router.push("/login");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Falha temporária.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="login-card card" onSubmit={submit}>
      <div><span className="eyebrow">Cadastro gratuito</span><h2>Crie sua conta</h2><p>Seu perfil começa como usuário comum.</p></div>
      <label>Nome<input name="name" required minLength={3} maxLength={120} autoComplete="name" /></label>
      <label>Usuário<input name="username" required minLength={3} maxLength={60} pattern="[a-zA-Z0-9_.-]+" autoComplete="username" /></label>
      <label>E-mail<input name="email" type="email" required autoComplete="email" /></label>
      <label>Senha<input name="password" type="password" required minLength={8} maxLength={128} autoComplete="new-password" /><small>Mínimo de 8 caracteres, com letra e número.</small></label>
      {error && <div className="notice error">{error}</div>}
      <button className="button primary full" disabled={loading}>{loading ? "Criando…" : "Criar conta"}</button>
      <p className="form-alternative">Já possui conta? <Link href="/login">Entrar</Link></p>
    </form>
  );
}
