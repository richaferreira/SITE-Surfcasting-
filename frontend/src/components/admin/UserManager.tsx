"use client";

import { useCallback, useEffect, useState } from "react";
import { adminRequest, jsonRequest } from "@/lib/admin-api";
import type { User } from "@/lib/types";

export function UserManager() {
  const [items, setItems] = useState<User[]>([]); const [error, setError] = useState(""); const [message, setMessage] = useState("");
  const load = useCallback(async () => { try { setItems((await adminRequest<{ items: User[] }>("users?limit=100")).items); } catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao carregar usuários."); } }, []);
  useEffect(() => { adminRequest<{ items: User[] }>("users?limit=100").then((data) => setItems(data.items)).catch((reason) => setError(reason instanceof Error ? reason.message : "Falha ao carregar usuários.")); }, []);
  async function update(user: User, change: { role?: User["role"]; is_active?: boolean }) { setError(""); setMessage(""); try { await adminRequest(`users/${user.id}`, jsonRequest("PATCH", change)); setMessage("Permissão atualizada."); await load(); } catch (reason) { setError(reason instanceof Error ? reason.message : "Falha ao atualizar usuário."); } }
  return <section className="manager-layout">{error && <div className="notice error">{error}</div>}{message && <div className="notice success">{message}</div>}<div className="admin-table-wrap card"><table className="admin-table"><thead><tr><th>Usuário</th><th>Papel</th><th>Status</th><th>Alterar papel</th><th><span className="sr-only">Ações</span></th></tr></thead><tbody>{items.map((user) => <tr key={user.id}><td><strong>{user.name}</strong><small>@{user.username} · {user.email}</small></td><td><span className={`role-pill ${user.role.toLowerCase()}`}>{user.role.toLowerCase()}</span></td><td>{user.is_active ? "Ativo" : "Inativo"}</td><td><select aria-label={`Papel de ${user.name}`} value={user.role} onChange={(event) => update(user, { role: event.target.value as User["role"] })}><option value="USER">Usuário</option><option value="AUTHOR">Autor</option><option value="ADMIN">Admin</option></select></td><td className="table-actions"><button onClick={() => update(user, { is_active: !user.is_active })}>{user.is_active ? "Desativar" : "Reativar"}</button></td></tr>)}</tbody></table></div></section>;
}
