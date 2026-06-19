"use client";

import { motion } from "framer-motion";
import { Loader2, Radio, RefreshCw } from "lucide-react";
import { FearGreedGauge } from "@/components/FearGreedGauge";
import { LogoMark } from "@/components/Logo";
import type { DashboardStatus } from "@/lib/types";

interface HeroSectionProps {
  data: DashboardStatus | null;
  loading: boolean;
  refreshing: boolean;
  onRefresh: () => void;
}

function regimeTone(label: string): string {
  const lower = label.toLowerCase();
  if (lower.includes("fear")) return "border-accent/50 text-accent";
  if (lower.includes("greed")) return "border-[#c8f135]/40 text-[#c8f135]";
  return "border-border text-foreground";
}

export function HeroSection({ data, loading, refreshing, onRefresh }: HeroSectionProps) {
  const fg = data?.signals.fear_greed;
  const regime = data?.regime_label ?? "—";
  const mcap = data?.perception?.raw?.global_metrics?.total_market_cap;

  const stats = [
    { label: "Chain", value: data?.chain ?? "BNB" },
    { label: "Mode", value: data?.dry_run ? "Dry Run" : "Live" },
    {
      label: "Market Cap",
      value: mcap ? `$${(mcap / 1e12).toFixed(2)}T` : "—",
    },
    { label: "Regime", value: data?.regime?.replaceAll("_", " ") ?? "—" },
  ];

  return (
    <motion.header
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
      className="panel-card panel-card-glow mb-8 overflow-hidden sm:mb-10"
    >
      <div className="panel-inner-glow pointer-events-none absolute inset-0" />
      <div className="relative px-5 py-8 sm:px-8 sm:py-10 md:px-10 md:py-12">
        <div className="flex flex-col gap-8 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex-1">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded border border-border bg-surface p-2 sm:h-14 sm:w-14">
                <LogoMark size={40} className="h-full w-full" />
              </div>
              <div>
                <div className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-muted">
                  <Radio className="h-3 w-3 text-accent" strokeWidth={2} />
                  Autonomous Market Mirror
                </div>
                <h1 className="font-display text-3xl font-medium tracking-wide sm:text-4xl md:text-5xl">
                  <span className="text-gradient">EchoTrader</span>
                </h1>
              </div>
            </div>
            <p className="mt-3 max-w-lg font-mono text-sm leading-relaxed text-muted">
              Perceive. Reason. Execute with discipline — the agent reads fear,
              divergence, and flow before every move.
            </p>
            <div className="mt-6 flex flex-wrap gap-2">
              {stats.map((stat) => (
                <div
                  key={stat.label}
                  className="stat-pill rounded px-3 py-2 font-mono text-[10px] uppercase tracking-[0.1em]"
                >
                  <span className="text-muted">{stat.label}</span>
                  <span className="ml-2 text-foreground">{stat.value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex flex-col items-center gap-5 sm:flex-row lg:flex-col xl:flex-row">
            <div className="text-center lg:text-right">
              <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-muted">
                Current Regime
              </div>
              <div
                className={`mt-2 inline-block rounded border px-4 py-2 font-display text-2xl tracking-wide sm:text-3xl ${regimeTone(regime)}`}
              >
                {loading && !data ? "—" : regime}
              </div>
            </div>
            <FearGreedGauge
              value={fg}
              label={data?.signals.fear_greed_label ?? undefined}
              size={128}
            />
          </div>
        </div>

        <div className="mt-8 flex flex-col gap-3 border-t border-border pt-6 sm:flex-row sm:items-center sm:justify-between">
          <p className="font-mono text-[11px] text-muted">
            {data?.timestamp
              ? `Last sync ${new Date(data.timestamp).toLocaleString()}`
              : "Awaiting first perception cycle"}
          </p>
          <button
            type="button"
            onClick={onRefresh}
            disabled={refreshing || loading}
            className="btn-primary flex items-center justify-center gap-2 rounded px-5 py-2.5 font-mono text-[11px] uppercase tracking-[0.14em]"
          >
            {refreshing ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Running cycle...
              </>
            ) : (
              <>
                <RefreshCw className="h-3.5 w-3.5" />
                Refresh Agent
              </>
            )}
          </button>
        </div>
      </div>
    </motion.header>
  );
}