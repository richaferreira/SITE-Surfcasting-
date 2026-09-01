import { UserManager } from "@/components/admin/UserManager";

export default function UsersAdminPage() {
  return <><header className="admin-page-header"><div><span className="eyebrow">RBAC</span><h1>Usuários e permissões</h1><p>Promova autores, controle acesso e preserve ao menos um administrador ativo.</p></div></header><UserManager /></>;
}
