"use client";

import { useEffect, useState } from "react";

import { browserApi, getStoredUser, logoutSession, restoreSession, SessionUser } from "../lib/api";

type NotificationItem = { id: number };

export default function SiteHeader() {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    setUser(getStoredUser());
    restoreSession().then((restored) => {
      setUser(restored);
      if (!restored) {
        setUnread(0);
        return;
      }
      browserApi<NotificationItem[]>("/api/v1/notifications?unread_only=true&limit=10", {}, true)
        .then((items) => setUnread(items.length))
        .catch(() => setUnread(0));
    });
  }, []);

  async function logout() {
    await logoutSession();
    setUser(null);
    setUnread(0);
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
            <a className="notificationButton" href="/notificacoes" aria-label={`${unread} notificações não lidas`}>
              Avisos{unread > 0 ? <b>{unread > 9 ? "9+" : unread}</b> : null}
            </a>
            <a className="profileButton" href="/perfil">{user.name.split(" ")[0]}</a>
            <button className="textButton" type="button" onClick={() => void logout()}>Sair</button>
          </>
        ) : (
          <a className="profileButton" href="/login">Entrar</a>
        )}
      </div>
    </header>
  );
}
