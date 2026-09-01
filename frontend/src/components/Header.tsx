import Link from "next/link";

export function Header() {
  return (
    <header className="site-header">
      <div className="shell header-inner">
        <Link className="brand" href="/" aria-label="Surfcasting Região dos Lagos — início">
          <span className="brand-mark" aria-hidden="true">SRL</span>
          <span><strong>Surfcasting</strong><small>Região dos Lagos</small></span>
        </Link>
        <nav className="desktop-nav" aria-label="Navegação principal">
          <Link href="/">Condições</Link>
          <Link href="/mapa">Mapa técnico</Link>
          <Link href="/academia">Academia</Link>
          <Link href="/comunidade">Comunidade</Link>
          <Link className="nav-cta" href="/login">Entrar</Link>
        </nav>
      </div>
      <nav className="mobile-nav" aria-label="Navegação móvel">
        <Link href="/"><span aria-hidden="true">≈</span>Condições</Link>
        <Link href="/mapa"><span aria-hidden="true">⌖</span>Mapa</Link>
        <Link href="/academia"><span aria-hidden="true">◇</span>Academia</Link>
        <Link href="/comunidade"><span aria-hidden="true">◌</span>Comunidade</Link>
        <Link href="/login"><span aria-hidden="true">○</span>Conta</Link>
      </nav>
    </header>
  );
}
