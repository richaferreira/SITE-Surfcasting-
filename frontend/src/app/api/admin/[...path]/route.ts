import { cookies } from "next/headers";
import { NextRequest, NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";

const allowedRoots = new Set(["beaches", "points", "posts", "media", "monitoring", "community", "ads", "users"]);

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const token = (await cookies()).get("srl_session")?.value;
  if (!token) return NextResponse.json({ detail: "Sessão ausente." }, { status: 401 });
  const { path } = await context.params;
  if (!path.length || !allowedRoots.has(path[0]) || path.some((part) => !/^[a-zA-Z0-9_-]+$/.test(part))) {
    return NextResponse.json({ detail: "Rota administrativa não permitida." }, { status: 404 });
  }

  const target = new URL(`${API_BASE_URL}/admin/${path.map(encodeURIComponent).join("/")}`);
  request.nextUrl.searchParams.forEach((value, key) => target.searchParams.append(key, value));
  const headers = new Headers({ Authorization: `Bearer ${token}`, Accept: "application/json" });
  const contentType = request.headers.get("content-type");
  if (contentType) headers.set("Content-Type", contentType);

  try {
    const upstream = await fetch(target, {
      method: request.method,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer(),
      cache: "no-store",
      signal: AbortSignal.timeout(30000),
      headers,
    });
    if (upstream.status === 204) return new NextResponse(null, { status: 204 });
    const payload = await upstream.json().catch(() => ({ detail: "Resposta inválida do serviço." }));
    return NextResponse.json(payload, { status: upstream.status });
  } catch {
    return NextResponse.json({ detail: "Servidor indisponível." }, { status: 503 });
  }
}

export const GET = proxy;
export const POST = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
