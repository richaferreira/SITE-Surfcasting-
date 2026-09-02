import SiteHeader from "../../components/SiteHeader";

export const metadata = {
  title: "Termos de Uso | Surfcasting Região dos Lagos",
  description: "Termos de uso da plataforma Surfcasting Região dos Lagos.",
};

export default function TermsPage() {
  return (
    <main>
      <SiteHeader />
      <article className="pageShell legalPage">
        <span className="eyebrow">Transparência</span>
        <h1>Termos de Uso</h1>
        <p>Última atualização: 2 de setembro de 2026.</p>
        <h2>1. Finalidade da plataforma</h2>
        <p>O Surfcasting Região dos Lagos reúne informações oceanográficas, conteúdo técnico e recursos comunitários para auxiliar o planejamento da pesca de praia. Informações meteorológicas, marítimas, scores e recomendações possuem caráter informativo e não substituem avaliação presencial, alertas oficiais, experiência do pescador ou regras das autoridades competentes.</p>
        <h2>2. Cadastro e segurança</h2>
        <p>O usuário deve fornecer informações verdadeiras, manter suas credenciais protegidas e comunicar qualquer uso indevido da conta. Contas utilizadas para fraude, spam, assédio ou violação destes termos podem ser limitadas, suspensas ou desativadas.</p>
        <h2>3. Conteúdo da comunidade</h2>
        <p>Ao publicar comentários, capturas, imagens ou outros conteúdos, o usuário declara possuir autorização para compartilhá-los e permanece responsável pelo material enviado. É proibido conteúdo ilícito, ofensivo, discriminatório, enganoso, que viole direitos de terceiros ou incentive condutas inseguras.</p>
        <h2>4. Moderação</h2>
        <p>A plataforma disponibiliza mecanismos de denúncia e moderação. Conteúdos podem ser ocultados ou removidos quando violarem estes termos ou representarem risco à comunidade. Denúncias são analisadas pelo backoffice administrativo.</p>
        <h2>5. Dados externos e disponibilidade</h2>
        <p>Parte da telemetria depende de provedores externos. A plataforma não garante disponibilidade ininterrupta, precisão absoluta ou permanência de dados fornecidos por terceiros. Quando um provedor estiver indisponível, o sistema poderá informar degradação parcial.</p>
        <h2>6. Uso responsável</h2>
        <p>O usuário deve observar condições do mar, sinalização, áreas restritas, legislação ambiental, períodos de defeso, tamanhos mínimos, limites de captura e demais normas aplicáveis.</p>
        <h2>7. Alterações</h2>
        <p>Estes termos podem ser atualizados para refletir mudanças legais, técnicas ou funcionais. Alterações relevantes serão comunicadas na própria plataforma.</p>
      </article>
    </main>
  );
}
