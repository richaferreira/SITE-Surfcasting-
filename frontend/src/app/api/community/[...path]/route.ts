import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const token = (await cookies()).get("srl_session")?.value;
  if (!token) return NextResponse.json({ detail: "Entre para participar da comunidade." }, { status: 401 });
  const { path } = await context.params;
  if (!path.length || path.some((part) => !/^[a-zA-Z0-9_-]+$/.test(part))) {
    return NextResponse.json({ detail: "Rota não permitida." }, { status: 404 });
  }
  try {
    const upstream = await fetch(`${API_BASE_URL}/community/${path.map(encodeURIComponent).join("/")}`, {
      method: request.method,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer(),
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
      headers: {
        Authorization: `Bearer ${token}`,
        Accept: "application/json",
        "Content-Type": request.headers.get("content-type") ?? "application/json",
      },
    });
    if (upstream.status === 204) return new NextResponse(null, { status: 204 });
    const data = await upstream.json().catch(() => ({ detail: "Resposta inválida do serviço." }));
    return NextResponse.json(data, { status: upstream.status });
  } catch {
    return NextResponse.json({ detail: "Servidor indisponível." }, { status: 503 });
  }
}

export const POST = proxy;
export const DELETE = proxy;
