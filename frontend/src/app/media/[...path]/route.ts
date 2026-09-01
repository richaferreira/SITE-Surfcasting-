import { NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";

const backendOrigin = API_BASE_URL.replace(/\/api\/v1\/?$/, "");

export async function GET(_: Request, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  if (path.length !== 1 || !/^[a-f0-9]{32}\.(webp|mp4)$/.test(path[0])) {
    return NextResponse.json({ detail: "Arquivo não encontrado." }, { status: 404 });
  }
  try {
    const upstream = await fetch(`${backendOrigin}/media/${path.map(encodeURIComponent).join("/")}`, {
      signal: AbortSignal.timeout(15000),
    });
    if (!upstream.ok || !upstream.body) {
      return NextResponse.json({ detail: "Arquivo não encontrado." }, { status: upstream.status });
    }
    const headers = new Headers({
      "Content-Type": upstream.headers.get("content-type") ?? "application/octet-stream",
      "Cache-Control": "public, max-age=31536000, immutable",
      "X-Content-Type-Options": "nosniff",
    });
    const contentLength = upstream.headers.get("content-length");
    if (contentLength) headers.set("Content-Length", contentLength);
    return new NextResponse(upstream.body, {
      status: 200,
      headers,
    });
  } catch {
    return NextResponse.json({ detail: "Servidor de mídia indisponível." }, { status: 503 });
  }
}
