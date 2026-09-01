import type { Metadata } from "next";
import { RegisterForm } from "@/components/RegisterForm";

export const metadata: Metadata = { title: "Criar conta" };

export default function RegisterPage() {
  return (
    <section className="login-page">
      <div className="shell login-grid">
        <div className="login-intro">
          <span className="eyebrow">Comunidade</span>
          <h1>Compartilhe leitura.<br /><em>Pesque com respeito.</em></h1>
          <p>Relatos, dúvidas e conhecimento local em um espaço moderado para pescadores de todos os níveis.</p>
        </div>
        <RegisterForm />
      </div>
    </section>
  );
}
