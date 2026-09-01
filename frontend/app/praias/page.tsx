import SiteHeader from "../../components/SiteHeader";
import { serverApi } from "../../lib/api";

type Beach = {
  id: number;
  name: string;
  slug: string;
  city: string;
  state: string;
  description?: string | null;
  latitude: number;
  longitude: number;
  sea_bearing_deg: number;
  beach_profile: string;
  accessibility_summary?: string | null;
};

export default async function BeachesPage() {
  const beaches = (await serverApi<Beach[]>("/api/v1/beaches")) ?? [];

  return (
    <main>
      <SiteHeader />
      <section className="pageShell">
        <div className="pageHeading">
          <span className="eyebrow">Mapa técnico da costa</span>
          <h1>Praias e pontos de pesca</h1>
          <p>Consulte orientação do mar, perfil da praia, acessos e pontos cadastrados pela equipe.</p>
        </div>

        {beaches.length === 0 ? (
          <div className="notice">Nenhuma praia publicada ainda. Um administrador pode cadastrar a primeira pelo backoffice/API.</div>
        ) : (
          <div className="cardGrid">
            {beaches.map((beach) => (
              <a className="panel beachCard" href={`/praias/${beach.slug}`} key={beach.id}>
                <div className="cardTopline">
                  <span>{beach.city} · {beach.state}</span>
                  <span className="tag">{beach.beach_profile.replaceAll("_", " ")}</span>
                </div>
                <h2>{beach.name}</h2>
                <p>{beach.description ?? beach.accessibility_summary ?? "Informações técnicas em atualização."}</p>
                <div className="coordinates">
                  <span>{beach.latitude.toFixed(4)}, {beach.longitude.toFixed(4)}</span>
                  <strong>Mar {beach.sea_bearing_deg.toFixed(0)}° →</strong>
                </div>
              </a>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
