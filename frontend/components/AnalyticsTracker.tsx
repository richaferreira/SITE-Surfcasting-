"use client";

import { usePathname } from "next/navigation";
import { useEffect } from "react";

import { browserApi } from "../lib/api";

function sessionId(): string {
  const key = "srl_analytics_session";
  const existing = window.sessionStorage.getItem(key);
  if (existing) return existing;
  const created = crypto.randomUUID();
  window.sessionStorage.setItem(key, created);
  return created;
}

export default function AnalyticsTracker() {
  const pathname = usePathname();

  useEffect(() => {
    if (!pathname || pathname.startsWith("/admin")) return;
    const beachMatch = pathname.match(/^\/praias\/([^/]+)$/);
    void browserApi("/api/v1/analytics/events", {
      method: "POST",
      body: JSON.stringify({
        event_name: "page_view",
        session_id: sessionId(),
        page_path: pathname,
        beach_slug: beachMatch?.[1] ?? null,
      }),
    }).catch(() => undefined);
  }, [pathname]);

  return null;
}
