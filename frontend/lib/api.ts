export const PUBLIC_API_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export const SERVER_API_URL =
  process.env.API_URL ?? PUBLIC_API_URL;

export type SessionUser = {
  id: number;
  name: string;
  username: string;
  email: string;
  role: "ADMIN" | "AUTHOR" | "USER";
  avatar_url?: string | null;
  bio?: string | null;
  email_verified: boolean;
};

export type AuthPayload = {
  authenticated: boolean;
  user: SessionUser;
};

let refreshPromise: Promise<AuthPayload> | null = null;

export function getStoredUser(): SessionUser | null {
  if (typeof window === "undefined") return null;
  const raw = window.localStorage.getItem("srl_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as SessionUser;
  } catch {
    return null;
  }
}

export function saveSession(payload: AuthPayload): void {
  window.localStorage.setItem("srl_user", JSON.stringify(payload.user));
}

export function updateStoredUser(user: SessionUser): void {
  window.localStorage.setItem("srl_user", JSON.stringify(user));
}

export function clearSession(): void {
  window.localStorage.removeItem("srl_user");
  // Limpa resíduos das versões anteriores do portal.
  window.localStorage.removeItem("srl_token");
  window.localStorage.removeItem("srl_refresh_token");
}

function readCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const prefix = `${encodeURIComponent(name)}=`;
  const part = document.cookie.split("; ").find((item) => item.startsWith(prefix));
  return part ? decodeURIComponent(part.slice(prefix.length)) : null;
}

function csrfHeaders(headers: Headers, method: string): void {
  if (["GET", "HEAD", "OPTIONS"].includes(method.toUpperCase())) return;
  const csrf = readCookie("srl_csrf");
  if (csrf) headers.set("X-CSRF-Token", csrf);
}

async function refreshSession(): Promise<AuthPayload> {
  if (refreshPromise) return refreshPromise;

  const headers = new Headers({ "Content-Type": "application/json" });
  csrfHeaders(headers, "POST");
  refreshPromise = fetch(`${PUBLIC_API_URL}/api/v1/auth/refresh`, {
    method: "POST",
    headers,
    credentials: "include",
  })
    .then(async (response) => {
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail ?? "Sua sessão expirou. Entre novamente.");
      const payload = data as AuthPayload;
      saveSession(payload);
      return payload;
    })
    .catch((error) => {
      clearSession();
      throw error;
    })
    .finally(() => {
      refreshPromise = null;
    });

  return refreshPromise;
}

async function performRequest<T>(
  path: string,
  init: RequestInit,
  authenticated: boolean,
  allowRefresh: boolean,
): Promise<T> {
  const headers = new Headers(init.headers);
  const method = (init.method ?? "GET").toUpperCase();
  const isFormData = typeof FormData !== "undefined" && init.body instanceof FormData;
  if (init.body && !isFormData && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  csrfHeaders(headers, method);

  const response = await fetch(`${PUBLIC_API_URL}${path}`, {
    ...init,
    headers,
    credentials: "include",
  });
  if (response.status === 401 && authenticated && allowRefresh) {
    await refreshSession();
    return performRequest<T>(path, init, authenticated, false);
  }
  if (response.status === 204) return undefined as T;

  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.detail ?? "Não foi possível concluir a operação.");
  return data as T;
}

export async function browserApi<T>(
  path: string,
  init: RequestInit = {},
  authenticated = false,
): Promise<T> {
  return performRequest<T>(path, init, authenticated, true);
}

export async function restoreSession(): Promise<SessionUser | null> {
  try {
    const user = await browserApi<SessionUser>("/api/v1/auth/me", {}, true);
    updateStoredUser(user);
    return user;
  } catch {
    clearSession();
    return null;
  }
}

export async function logoutSession(): Promise<void> {
  const headers = new Headers({ "Content-Type": "application/json" });
  csrfHeaders(headers, "POST");
  try {
    await fetch(`${PUBLIC_API_URL}/api/v1/auth/logout`, {
      method: "POST",
      headers,
      credentials: "include",
    });
  } finally {
    clearSession();
  }
}

export async function serverApi<T>(path: string): Promise<T | null> {
  try {
    const response = await fetch(`${SERVER_API_URL}${path}`, { next: { revalidate: 120 } });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}
