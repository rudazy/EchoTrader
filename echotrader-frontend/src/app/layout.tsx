import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { SiteBackground } from "@/components/SiteBackground";
import { ThemeProvider } from "@/components/ThemeProvider";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  metadataBase: new URL(
    process.env.NEXT_PUBLIC_SITE_URL ?? "https://echotrader.vercel.app",
  ),
  title: "EchoTrader | Market Mirror",
  description:
    "Autonomous reflexive trading agent dashboard — perception, reasoning, and self-custody execution on BNB Chain.",
  icons: {
    icon: [{ url: "/icon.svg", type: "image/svg+xml" }],
    apple: [{ url: "/apple-icon.svg", type: "image/svg+xml" }],
  },
  openGraph: {
    title: "EchoTrader | Market Mirror",
    description:
      "Institutional-grade dashboard for the EchoTrader autonomous market mirror agent.",
    type: "website",
    images: [{ url: "/og.svg", width: 1200, height: 630, alt: "EchoTrader" }],
  },
  twitter: {
    card: "summary_large_image",
    title: "EchoTrader | Market Mirror",
    description:
      "Autonomous reflexive trading agent — perceive, reason, execute with self-custody.",
    images: ["/og.svg"],
  },
};

const themeInitScript = `
(function () {
  try {
    var stored = localStorage.getItem('echotrader-theme');
    if (stored === 'light') document.documentElement.classList.add('light');
  } catch (e) {}
})();
`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
      </head>
      <body className="min-h-full bg-background text-foreground">
        <ThemeProvider>
          <SiteBackground />
          <div className="relative min-h-screen overflow-hidden">{children}</div>
        </ThemeProvider>
      </body>
    </html>
  );
}