import { cookies } from "next/headers";
import { NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";

export async function GET() {
  const token = (await cookies()).get("srl_session")?.value;
  if (!token) return NextResponse.json({ detail: "Sessão ausente." }, { status: 401 });
  try {
    const upstream = await fetch(`${API_BASE_URL}/auth/me`, {
      cache: "no-store",
      signal: AbortSignal.timeout(8000),
      headers: { Authorization: `Bearer ${token}`, Accept: "application/json" },
    });
    const payload = await upstream.json().catch(() => ({ detail: "Sessão inválida." }));
    const response = NextResponse.json(payload, { status: upstream.status });
    if (upstream.status === 401) response.cookies.set("srl_session", "", { path: "/", maxAge: 0 });
    return response;
  } catch {
    return NextResponse.json({ detail: "Servidor indisponível." }, { status: 503 });
  }
}
