import Link from "next/link";

export function Footer() {
  return (
    <footer className="site-footer">
      <div className="shell footer-grid">
        <div>
          <strong>Surfcasting Região dos Lagos</strong>
          <p>Dados para decidir. Técnica para evoluir. Respeito ao mar sempre.</p>
        </div>
        <nav aria-label="Links do rodapé">
          <Link href="/mapa">Mapa técnico</Link>
          <Link href="/academia">Academia Long Cast</Link>
          <Link href="/comunidade">Comunidade</Link>
          <Link href="/admin">Backoffice</Link>
        </nav>
        <p className="data-note">O score é orientativo. Confira avisos oficiais e observe o mar no local.</p>
      </div>
    </footer>
  );
}
