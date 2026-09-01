import Link from "next/link";

export default function OfflinePage() {
  return (
    <section className="shell state-page">
      <span className="eyebrow">Modo praia</span>
      <h1>Você está sem conexão.</h1>
      <p>As páginas abertas anteriormente continuam disponíveis. Dados ao vivo e ações do backoffice precisam de internet.</p>
      <Link className="button primary" href="/">Voltar ao painel</Link>
    </section>
  );
}
