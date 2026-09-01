import { NewThreadForm } from "@/components/NewThreadForm";
import { getBeaches } from "@/lib/api";

export default async function NewThreadPage() {
  const { items } = await getBeaches();
  return (
    <section className="shell new-thread-page">
      <div><span className="eyebrow">Nova discussão</span><h1>Compartilhe uma leitura útil.</h1><p>Explique condições e limitações. Evite afirmar que um ponto está seguro ou produtivo sem contexto.</p></div>
      <NewThreadForm beaches={items} />
    </section>
  );
}
