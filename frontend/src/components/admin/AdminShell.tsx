"use client";

import type { Route } from "next";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import type { User } from "@/lib/types";

const nav: ReadonlyArray<{ href: Route; label: string; icon: string; roles: ReadonlyArray<User["role"]> }> = [
  { href: "/admin", label: "Visão geral", icon: "◫", roles: ["ADMIN"] },
  { href: "/admin/praias", label: "Praias", icon: "≈", roles: ["ADMIN"] },
  { href: "/admin/pontos", label: "Pontos de pesca", icon: "⌖", roles: ["ADMIN"] },
  { href: "/admin/conteudos", label: "Conteúdos", icon: "◇", roles: ["ADMIN", "AUTHOR"] },
  { href: "/admin/comunidade", label: "Comunidade", icon: "◌", roles: ["ADMIN"] },
  { href: "/admin/midia", label: "Mídia", icon: "▧", roles: ["ADMIN", "AUTHOR"] },
  { href: "/admin/anuncios", label: "Anúncios", icon: "▤", roles: ["ADMIN"] },
  { href: "/admin/usuarios", label: "Usuários", icon: "◎", roles: ["ADMIN"] },
  { href: "/admin/monitoramento", label: "Monitoramento", icon: "↗", roles: ["ADMIN"] },
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    fetch("/api/auth/me", { cache: "no-store" }).then(async (response) => {
      if (!response.ok) { router.replace(`/login?next=${encodeURIComponent(pathname)}`); return; }
      const profile = (await response.json()) as User;
      setUser(profile);
      if (profile.role === "USER") router.replace("/comunidade");
      else if (profile.role === "AUTHOR" && !["/admin/conteudos", "/admin/midia"].includes(pathname)) {
        router.replace("/admin/conteudos");
      }
    }).catch(() => undefined);
  }, [pathname, router]);

  async function logout() {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  }

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div><span className="eyebrow">Backoffice</span><strong>Central de operação</strong></div>
        <nav aria-label="Navegação administrativa">
          {nav.filter((item) => user && item.roles.includes(user.role)).map((item) => (
            <Link className={pathname === item.href ? "active" : ""} href={item.href} key={item.href}><span aria-hidden="true">{item.icon}</span>{item.label}</Link>
          ))}
        </nav>
        <div className="admin-user">
          <i>{user?.name?.slice(0, 2).toUpperCase() ?? "…"}</i>
          <span><strong>{user?.name ?? "Validando sessão"}</strong><small>{user?.role ?? ""}</small></span>
          <button type="button" onClick={logout} aria-label="Sair">↪</button>
        </div>
      </aside>
      <div className="admin-content">{children}</div>
    </div>
  );
}
