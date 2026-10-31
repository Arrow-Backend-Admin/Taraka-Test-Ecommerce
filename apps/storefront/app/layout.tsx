import type { Metadata } from "next";
import localFont from "next/font/local";

import "./globals.css";

const archivo = localFont({
  src: "./fonts/Archivo-Variable.ttf",
  variable: "--font-archivo",
  weight: "100 900",
  display: "swap",
  fallback: ["Segoe UI", "Arial", "sans-serif"],
});

const inter = localFont({
  src: "./fonts/Inter-Variable.ttf",
  variable: "--font-inter",
  weight: "100 900",
  display: "swap",
  fallback: ["Segoe UI", "Arial", "sans-serif"],
});

const notoSansDevanagari = localFont({
  src: "./fonts/NotoSansDevanagari-Variable.ttf",
  variable: "--font-noto-deva",
  weight: "100 900",
  display: "swap",
  fallback: ["Nirmala UI", "sans-serif"],
});

const notoSerifDevanagari = localFont({
  src: "./fonts/NotoSerifDevanagari-Variable.ttf",
  variable: "--font-noto-serif-deva",
  weight: "100 900",
  display: "swap",
  fallback: ["Nirmala UI", "serif"],
});

export const metadata: Metadata = {
  title: "Sāntvana — concept storefront",
  description:
    "Phase 4 Milestone 1 concept storefront for Sāntvana, with the Phase 2 brand system and a publish-gated catalogue.",
  robots: {
    index: false,
    follow: false,
  },
  icons: {
    icon: "/brand/logos/santvana-monogram.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${archivo.variable} ${inter.variable} ${notoSansDevanagari.variable} ${notoSerifDevanagari.variable}`}
    >
      <body>{children}</body>
    </html>
  );
}
