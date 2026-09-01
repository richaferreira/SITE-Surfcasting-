export async function adminRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`/api/admin/${path}`, { cache: "no-store", ...init });
  if (response.status === 204) return undefined as T;
  const payload = await response.json().catch(() => ({ detail: "Resposta inválida do serviço." }));
  if (!response.ok) {
    const detail = Array.isArray(payload.detail)
      ? payload.detail.map((item: { msg?: string }) => item.msg ?? "Campo inválido").join("; ")
      : payload.detail;
    throw new Error(detail ?? "Não foi possível concluir a operação.");
  }
  return payload as T;
}

export const jsonRequest = (method: "POST" | "PATCH", body: unknown): RequestInit => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});
