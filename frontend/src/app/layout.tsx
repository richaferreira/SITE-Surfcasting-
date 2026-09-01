import type { Metadata, Viewport } from "next";
import Link from "next/link";
import { Footer } from "@/components/Footer";
import { Header } from "@/components/Header";
import { PwaRegister } from "@/components/PwaRegister";
import "maplibre-gl/dist/maplibre-gl.css";
import "./globals.css";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://localhost:3000";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: { default: "Surfcasting Região dos Lagos", template: "%s | Surfcasting Região dos Lagos" },
  description: "Condições do mar, mapa técnico e conhecimento long cast para a Região dos Lagos.",
  applicationName: "Surfcasting Região dos Lagos",
  manifest: "/manifest.webmanifest",
  alternates: { canonical: "/" },
  openGraph: {
    type: "website",
    locale: "pt_BR",
    siteName: "Surfcasting Região dos Lagos",
    title: "Surfcasting Região dos Lagos",
    description: "Telemetria, leitura de praia e técnica long cast em um só lugar.",
  },
};

export const viewport: Viewport = {
  themeColor: "#071d26",
  colorScheme: "dark",
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>
        <Link className="skip-link" href="#conteudo">Ir para o conteúdo</Link>
        <Header />
        <main id="conteudo">{children}</main>
        <Footer />
        <PwaRegister />
      </body>
    </html>
  );
}
