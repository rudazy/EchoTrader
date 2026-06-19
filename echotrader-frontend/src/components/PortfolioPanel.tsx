"use client";

import { motion } from "framer-motion";
import { Wallet } from "lucide-react";
import { PanelCard } from "@/components/PanelCard";
import type { DashboardStatus } from "@/lib/types";

interface PortfolioPanelProps {
  data: DashboardStatus | null;
}

export function PortfolioPanel({ data }: PortfolioPanelProps) {
  const portfolio = data?.portfolio;
  const risk = data?.risk;
  const deployed = portfolio?.deployed_pct ?? 0;

  return (
    <PanelCard
      title="Portfolio"
      subtitle={portfolio?.network?.toUpperCase() ?? "BSC"}
      icon={<Wallet className="h-4 w-4 text-accent" strokeWidth={1.75} />}
      className="lg:col-span-4"
      delay={0.22}
    >
      <div className="space-y-5 font-mono text-sm">
        <div>
          <div className="text-[10px] uppercase tracking-[0.14em] text-muted">
            Allocated Capital
          </div>
          <div className="mt-1 font-display text-3xl text-foreground">
            ${portfolio?.allocated_capital_usd?.toLocaleString() ?? "—"}
          </div>
        </div>

        <div>
          <div className="mb-2 flex justify-between text-[10px] uppercase tracking-[0.14em] text-muted">
            <span>Deployed</span>
            <span className="text-foreground">{deployed}%</span>
          </div>
          <div className="signal-bar h-2">
            <motion.div
              className="signal-bar-fill"
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(deployed, 100)}%` }}
              transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
            />
          </div>
        </div>

        <div className="flex items-center justify-between rounded border border-border/80 bg-background/40 px-4 py-3">
          <div>
            <div className="text-[10px] uppercase tracking-[0.14em] text-muted">
              Primary Token
            </div>
            <div className="mt-1 text-xl text-accent">{portfolio?.token ?? "—"}</div>
          </div>
          <div
            className={`rounded border px-2 py-1 text-[10px] uppercase tracking-[0.1em] ${
              risk?.approved
                ? "border-accent/40 text-accent"
                : "border-border text-muted"
            }`}
          >
            {risk?.approved ? "Approved" : "Blocked"}
          </div>
        </div>

        {risk?.reasons?.[0] && (
          <p className="font-mono text-[11px] leading-relaxed text-muted">
            {risk.reasons[0]}
          </p>
        )}
      </div>
    </PanelCard>
  );
}