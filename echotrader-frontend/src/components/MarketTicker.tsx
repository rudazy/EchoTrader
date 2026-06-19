"use client";

import type { DashboardStatus } from "@/lib/types";

interface MarketTickerProps {
  data: DashboardStatus | null;
}

export function MarketTicker({ data }: MarketTickerProps) {
  const items = [
    `Fear/Greed ${data?.signals.fear_greed ?? "—"}`,
    `BTC Dom ${data?.signals.btc_dominance?.toFixed(1) ?? "—"}%`,
    `Regime ${data?.regime_label ?? "—"}`,
    `Chain ${data?.chain ?? "BNB"}`,
    `Action ${(data?.decision?.action ?? "hold").toUpperCase()}`,
    `Confidence ${data?.reasoner?.confidence_pct ?? "—"}%`,
  ];

  const doubled = [...items, ...items];

  return (
    <div className="relative mb-6 overflow-hidden border-y border-border/80 py-2.5 sm:mb-8">
      <div className="pointer-events-none absolute left-0 top-0 z-10 h-full w-16 bg-gradient-to-r from-background to-transparent" />
      <div className="pointer-events-none absolute right-0 top-0 z-10 h-full w-16 bg-gradient-to-l from-background to-transparent" />
      <div className="animate-marquee flex w-max gap-8 font-mono text-[10px] uppercase tracking-[0.16em] text-muted">
        {doubled.map((item, i) => (
          <span key={`${item}-${i}`} className="flex items-center gap-8">
            <span className="text-foreground/90">{item}</span>
            <span className="text-accent/60">◆</span>
          </span>
        ))}
      </div>
    </div>
  );
}