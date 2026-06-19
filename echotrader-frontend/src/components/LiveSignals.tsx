"use client";

import { motion } from "framer-motion";
import { Activity } from "lucide-react";
import { PanelCard } from "@/components/PanelCard";
import type { DashboardStatus } from "@/lib/types";

interface LiveSignalsProps {
  data: DashboardStatus | null;
}

function signalFill(label: string, value: string): number {
  const n = parseFloat(value);
  if (label === "Fear & Greed" && !Number.isNaN(n)) return n;
  if (label === "BTC Dominance" && !Number.isNaN(n)) return n;
  if (label === "Social Heat" && !Number.isNaN(n)) return n * 100;
  if (value === "bullish" || value === "inflow") return 75;
  if (value === "bearish" || value === "outflow") return 25;
  return 50;
}

function SignalRow({
  label,
  value,
  sub,
  index,
}: {
  label: string;
  value: string;
  sub?: string;
  index: number;
}) {
  const fill = signalFill(label, value);

  return (
    <motion.div
      initial={{ opacity: 0, x: -8 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: 0.1 + index * 0.06 }}
      className="group rounded border border-transparent px-3 py-3 transition hover:border-border hover:bg-background/30"
    >
      <div className="flex items-baseline justify-between gap-3">
        <div className="font-mono text-2xl text-foreground sm:text-3xl">{value}</div>
        {sub && (
          <span className="font-mono text-[10px] uppercase tracking-[0.12em] text-accent">
            {sub}
          </span>
        )}
      </div>
      <div className="mt-2 font-mono text-[10px] uppercase tracking-[0.14em] text-muted">
        {label}
      </div>
      <div className="signal-bar mt-2">
        <motion.div
          className="signal-bar-fill"
          initial={{ width: 0 }}
          animate={{ width: `${fill}%` }}
          transition={{ duration: 0.9, delay: 0.15 + index * 0.05, ease: [0.22, 1, 0.36, 1] }}
        />
      </div>
    </motion.div>
  );
}

export function LiveSignals({ data }: LiveSignalsProps) {
  const signals = data?.signals;
  const fg = signals?.fear_greed ?? "—";
  const divergence = signals?.divergence_score ?? "neutral";
  const btcDom = signals?.btc_dominance?.toFixed(1) ?? "—";
  const social = signals?.social_heat?.toFixed(2) ?? "—";
  const flow = signals?.onchain_flow ?? "—";

  const rows = [
    {
      label: "Fear & Greed",
      value: String(fg),
      sub: signals?.fear_greed_label ?? undefined,
    },
    { label: "Divergence", value: divergence.replaceAll("_", " ") },
    { label: "BTC Dominance", value: `${btcDom}%` },
    { label: "Social Heat", value: String(social) },
    { label: "On-Chain Flow", value: flow.replaceAll("_", " ") },
  ];

  return (
    <PanelCard
      title="Live Signals"
      subtitle="Real-time perception feed"
      icon={<Activity className="h-4 w-4 text-accent" strokeWidth={1.75} />}
      className="lg:col-span-4"
      delay={0.12}
    >
      <div className="space-y-1">
        {rows.map((row, i) => (
          <SignalRow key={row.label} {...row} index={i} />
        ))}
      </div>
    </PanelCard>
  );
}