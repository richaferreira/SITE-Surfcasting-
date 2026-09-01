"use client";

import { useEffect, useState } from "react";

import { clearSession, getStoredUser, SessionUser } from "../lib/api";

export default function SiteHeader() {
  const [user, setUser] = useState<SessionUser | null>(null);

  useEffect(() => {
    setUser(getStoredUser());
  }, []);

  function logout() {
    clearSession();
    setUser(null);
    window.location.href = "/";
  }

  return (
    <header className="topbar">
      <a className="brand" href="/" aria-label="Surfcasting Região dos Lagos - início">
        <span className="brandMark" aria-hidden="true">SRL</span>
        <span>
          <strong>Surfcasting</strong>
          <small>Região dos Lagos</small>
        </span>
      </a>
      <nav className="desktopNav" aria-label="Navegação principal">
        <a href="/">Condições</a>
        <a href="/praias">Praias</a>
        <a href="/comunidade">Comunidade</a>
        {user?.role === "ADMIN" ? <a href="/admin">Admin</a> : null}
      </nav>
      <div className="headerAccount">
        {user ? (
          <>
            <a className="profileButton" href="/perfil">{user.name.split(" ")[0]}</a>
            <button className="textButton" type="button" onClick={logout}>Sair</button>
          </>
        ) : (
          <a className="profileButton" href="/login">Entrar</a>
        )}
      </div>
    </header>
  );
}
