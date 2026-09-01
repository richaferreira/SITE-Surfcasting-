import { NextRequest, NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";

const allowedRoots = new Set(["beaches", "fishing-score", "academy", "community", "ads"]);

export async function GET(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  if (!path.length || !allowedRoots.has(path[0]) || path.some((part) => !/^[a-zA-Z0-9_-]+$/.test(part))) {
    return NextResponse.json({ detail: "Rota pública não permitida." }, { status: 404 });
  }
  const target = new URL(`${API_BASE_URL}/${path.map(encodeURIComponent).join("/")}`);
  request.nextUrl.searchParams.forEach((value, key) => target.searchParams.append(key, value));
  try {
    const upstream = await fetch(target, {
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
      headers: { Accept: "application/json" },
    });
    const payload = await upstream.json().catch(() => ({ detail: "Resposta inválida do serviço." }));
    return NextResponse.json(payload, { status: upstream.status });
  } catch {
    return NextResponse.json({ detail: "Serviço temporariamente indisponível." }, { status: 503 });
  }
}
