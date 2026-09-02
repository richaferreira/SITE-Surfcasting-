"use client";

import { useEffect, useState } from "react";

import SiteHeader from "../../components/SiteHeader";
import { browserApi } from "../../lib/api";

type NotificationItem = {
  id: number;
  notification_type: string;
  title: string;
  message: string;
  action_url: string | null;
  read_at: string | null;
  created_at: string;
};

export default function NotificationsPage() {
  const [items, setItems] = useState<NotificationItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  function load() {
    browserApi<NotificationItem[]>("/api/v1/notifications?limit=100", {}, true)
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err.message : "Não foi possível carregar as notificações."));
  }

  useEffect(load, []);

  async function markRead(id: number) {
    await browserApi(`/api/v1/notifications/${id}/read`, { method: "POST" }, true);
    setItems((current) => current.map((item) => item.id === id ? { ...item, read_at: new Date().toISOString() } : item));
  }

  async function markAll() {
    await browserApi("/api/v1/notifications/read-all", { method: "POST" }, true);
    const now = new Date().toISOString();
    setItems((current) => current.map((item) => ({ ...item, read_at: item.read_at ?? now })));
  }

  return (
    <main>
      <SiteHeader />
      <section className="pageShell">
        <div className="pageHeading actionHeading">
          <div>
            <span className="eyebrow">Sua conta</span>
            <h1>Notificações</h1>
            <p>Comentários, curtidas e avisos importantes da comunidade aparecem aqui.</p>
          </div>
          <button className="secondaryButton" type="button" onClick={() => void markAll()}>Marcar todas como lidas</button>
        </div>
        {error ? <div className="notice errorNotice">{error}</div> : null}
        <div className="notificationList">
          {items.length === 0 ? <div className="panel emptyState">Você ainda não possui notificações.</div> : null}
          {items.map((item) => (
            <article key={item.id} className={`panel notificationCard ${item.read_at ? "isRead" : "isUnread"}`}>
              <div>
                <span className="eyebrow">{item.notification_type.replaceAll("_", " ")}</span>
                <h2>{item.title}</h2>
                <p>{item.message}</p>
                <small>{new Date(item.created_at).toLocaleString("pt-BR")}</small>
              </div>
              <div className="notificationActions">
                {item.action_url ? <a className="secondaryButton" href={item.action_url}>Abrir</a> : null}
                {!item.read_at ? <button className="textButton" type="button" onClick={() => void markRead(item.id)}>Marcar como lida</button> : null}
              </div>
            </article>
          ))}
        </div>
      </section>
    </main>
  );
}
