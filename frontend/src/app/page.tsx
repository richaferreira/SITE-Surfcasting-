import { DashboardClient } from "@/components/dashboard/DashboardClient";
import { AdSlot } from "@/components/AdSlot";
import { getAds, getBeaches } from "@/lib/api";

export default async function HomePage() {
  const [beaches, ads] = await Promise.all([getBeaches(), getAds("HOME_CONTEUDO")]);
  return <><DashboardClient beaches={beaches.items} initialDemo={beaches.demo} /><AdSlot ads={ads} /></>;
}
