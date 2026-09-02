import SiteHeader from "../../components/SiteHeader";

export const metadata = { title: "Sem conexão" };

export default function OfflinePage() {
  return (
    <main>
      <SiteHeader />
      <section className="pageShell authShell">
        <div className="authIntro">
          <span className="eyebrow">Modo offline</span>
          <h1>Sem conexão no momento.</h1>
          <p>Algumas páginas já visitadas podem continuar disponíveis. Telemetria, autenticação, comunidade e dados em tempo real exigem conexão.</p>
          <a className="primaryButton" href="/">Tentar novamente</a>
        </div>
      </section>
    </main>
  );
}
