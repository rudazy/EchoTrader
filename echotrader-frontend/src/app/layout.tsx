import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { SiteBackground } from "@/components/SiteBackground";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "EchoTrader | Market Mirror",
  description:
    "Autonomous reflexive trading agent dashboard — perception, reasoning, and self-custody execution on BNB Chain.",
  openGraph: {
    title: "EchoTrader | Market Mirror",
    description:
      "Institutional-grade dashboard for the EchoTrader autonomous market mirror agent.",
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
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full">
        <SiteBackground />
        {children}
      </body>
    </html>
  );
}