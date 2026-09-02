import type { Metadata, Viewport } from "next";
import "leaflet/dist/leaflet.css";
import "./globals.css";
import "./portal.css";
import "./launch-ready.css";

import AnalyticsTracker from "../components/AnalyticsTracker";
import PWARegister from "../components/PWARegister";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Surfcasting Região dos Lagos",
    template: "%s | Surfcasting Região dos Lagos",
  },
  description: "Condições do mar, vento, maré, praias, comunidade e inteligência para pesca de praia na Região dos Lagos.",
  applicationName: "Surfcasting Região dos Lagos",
  manifest: "/manifest.webmanifest",
  icons: {
    icon: "/icons/icon.svg",
    apple: "/icons/icon.svg",
  },
  openGraph: {
    type: "website",
    locale: "pt_BR",
    siteName: "Surfcasting Região dos Lagos",
    title: "Surfcasting Região dos Lagos",
    description: "Telemetria oceanográfica, Score de Pesca, praias, spots e comunidade de surfcasting.",
    url: siteUrl,
  },
  twitter: {
    card: "summary",
    title: "Surfcasting Região dos Lagos",
    description: "Condições e inteligência para pesca de praia na Região dos Lagos.",
  },
};

export const viewport: Viewport = {
  themeColor: "#071318",
  colorScheme: "dark",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>
        {children}
        <AnalyticsTracker />
        <PWARegister />
      </body>
    </html>
  );
}
