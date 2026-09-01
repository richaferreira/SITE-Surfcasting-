import { NextRequest, NextResponse } from "next/server";
import { API_BASE_URL } from "@/lib/api";

export async function POST(request: NextRequest) {
  try {
    const payload = await request.json();
    const upstream = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      body: JSON.stringify(payload),
      cache: "no-store",
      signal: AbortSignal.timeout(10000),
      headers: { "Content-Type": "application/json", Accept: "application/json" },
    });
    const data = await upstream.json().catch(() => ({ detail: "Resposta inválida do serviço." }));
    return NextResponse.json(data, { status: upstream.status });
  } catch {
    return NextResponse.json({ detail: "Não foi possível criar a conta." }, { status: 503 });
  }
}
