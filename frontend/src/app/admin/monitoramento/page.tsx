import { MonitoringDashboard } from "@/components/admin/MonitoringDashboard";

export default function MonitoringAdminPage() {
  return <><header className="admin-page-header"><div><span className="eyebrow">Observabilidade</span><h1>Monitoramento</h1><p>Tráfego, latência e consumo das integrações externas.</p></div></header><MonitoringDashboard /></>;
}
