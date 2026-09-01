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
};

export type AuthPayload = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: SessionUser;
};

let refreshPromise: Promise<AuthPayload> | null = null;

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("srl_token");
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return window.localStorage.getItem("srl_refresh_token");
}

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
  window.localStorage.setItem("srl_token", payload.access_token);
  window.localStorage.setItem("srl_refresh_token", payload.refresh_token);
  window.localStorage.setItem("srl_user", JSON.stringify(payload.user));
}

export function updateStoredUser(user: SessionUser): void {
  window.localStorage.setItem("srl_user", JSON.stringify(user));
}

export function clearSession(): void {
  window.localStorage.removeItem("srl_token");
  window.localStorage.removeItem("srl_refresh_token");
  window.localStorage.removeItem("srl_user");
}

async function refreshSession(): Promise<AuthPayload> {
  if (refreshPromise) return refreshPromise;
  const refreshToken = getRefreshToken();
  if (!refreshToken) throw new Error("Sua sessão expirou. Entre novamente.");

  refreshPromise = fetch(`${PUBLIC_API_URL}/api/v1/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
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
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");

  if (authenticated) {
    const token = getToken();
    if (!token) throw new Error("Faça login para continuar.");
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${PUBLIC_API_URL}${path}`, { ...init, headers });
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

export async function logoutSession(): Promise<void> {
  const refreshToken = getRefreshToken();
  if (refreshToken) {
    try {
      await fetch(`${PUBLIC_API_URL}/api/v1/auth/logout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });
    } finally {
      clearSession();
    }
  } else {
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
