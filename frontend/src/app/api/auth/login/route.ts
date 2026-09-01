import { NextRequest, NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";

export async function POST(request: NextRequest) {
  let credentials: { username?: string; password?: string };
  try {
    credentials = (await request.json()) as { username?: string; password?: string };
  } catch {
    return NextResponse.json({ detail: "Dados de acesso inválidos." }, { status: 400 });
  }
  if (!credentials.username || !credentials.password) {
    return NextResponse.json({ detail: "Informe usuário e senha." }, { status: 422 });
  }

  const form = new URLSearchParams({ username: credentials.username, password: credentials.password });
  try {
    const upstream = await fetch(`${API_BASE_URL}/auth/token`, {
      method: "POST",
      body: form,
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
      headers: { "Content-Type": "application/x-www-form-urlencoded", Accept: "application/json" },
    });
    const payload = await upstream.json().catch(() => ({ detail: "Resposta inválida do serviço." }));
    if (!upstream.ok) return NextResponse.json(payload, { status: upstream.status });

    const response = NextResponse.json({ user: payload.user });
    response.cookies.set("srl_session", payload.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      path: "/",
      maxAge: payload.expires_in,
    });
    return response;
  } catch {
    return NextResponse.json({ detail: "Não foi possível acessar o servidor." }, { status: 503 });
  }
}
