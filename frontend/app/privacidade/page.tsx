import SiteHeader from "../../components/SiteHeader";

export const metadata = {
  title: "Política de Privacidade | Surfcasting Região dos Lagos",
  description: "Política de privacidade e tratamento de dados pessoais da plataforma Surfcasting Região dos Lagos.",
};

export default function PrivacyPage() {
  return (
    <main>
      <SiteHeader />
      <article className="pageShell legalPage">
        <span className="eyebrow">LGPD</span>
        <h1>Política de Privacidade</h1>
        <p>Última atualização: 2 de setembro de 2026.</p>
        <h2>1. Dados tratados</h2>
        <p>Podemos tratar nome, nome de usuário, e-mail, avatar, biografia, registros de autenticação, preferências, praias favoritas, publicações, comentários, capturas, denúncias e eventos técnicos de navegação necessários à operação e melhoria do serviço.</p>
        <h2>2. Finalidades</h2>
        <p>Os dados são utilizados para criar e proteger contas, fornecer funcionalidades personalizadas, permitir participação na comunidade, moderar conteúdo, prevenir abuso, medir desempenho do portal, responder solicitações e manter a segurança operacional.</p>
        <h2>3. Bases legais</h2>
        <p>O tratamento pode ocorrer para execução do serviço solicitado pelo usuário, cumprimento de obrigação legal ou regulatória, exercício regular de direitos, legítimo interesse relacionado à segurança e melhoria do serviço e, quando aplicável, consentimento.</p>
        <h2>4. Cookies e sessão</h2>
        <p>A autenticação utiliza cookies de sessão HttpOnly e cookie técnico anti-CSRF. Tokens de autenticação não são persistidos no armazenamento local do navegador. Cookies estritamente necessários são usados para segurança e funcionamento da conta.</p>
        <h2>5. Analytics</h2>
        <p>O portal registra eventos técnicos próprios, como páginas acessadas e consultas a praias, para avaliar uso e estabilidade. Esses registros são mantidos no banco da plataforma e não dependem de rastreadores publicitários de terceiros.</p>
        <h2>6. Compartilhamento</h2>
        <p>Dados pessoais não são comercializados. Informações podem ser processadas por infraestrutura contratada necessária à hospedagem, e-mail transacional, banco de dados e segurança, sempre limitada à finalidade do serviço.</p>
        <h2>7. Retenção e segurança</h2>
        <p>São aplicadas medidas como hash de senha, tokens rotativos, cookies HttpOnly, proteção CSRF, controle de acesso, auditoria e backups. Os dados são mantidos pelo período necessário às finalidades informadas e às obrigações aplicáveis.</p>
        <h2>8. Direitos do titular</h2>
        <p>Nos termos da LGPD, o titular pode solicitar confirmação e acesso, correção, anonimização ou eliminação quando cabível, informação sobre compartilhamento, portabilidade nos limites legais e revogação de consentimento. Solicitações devem ser feitas pelo canal administrativo disponibilizado pela plataforma.</p>
        <h2>9. Exclusão da conta</h2>
        <p>Pedidos de exclusão serão avaliados considerando obrigações legais, prevenção de fraude, registros de auditoria e conteúdo comunitário. Quando necessário, dados poderão ser anonimizados em vez de eliminados imediatamente.</p>
      </article>
    </main>
  );
}
