"use client";

import { motion } from "framer-motion";
import { Brain, Target } from "lucide-react";
import { PanelCard } from "@/components/PanelCard";
import type { DashboardStatus } from "@/lib/types";

interface AgentThoughtProps {
  data: DashboardStatus | null;
}

export function AgentThought({ data }: AgentThoughtProps) {
  const read =
    data?.reasoner?.market_read ??
    "Waiting for agent perception cycle. Signals will appear here.";
  const reasoning = data?.reasoner?.reasoning ?? data?.reasoner?.risk_notes ?? "";
  const action = (data?.decision?.action ?? "hold").toUpperCase();
  const token = data?.decision?.token ?? "—";
  const confidence =
    data?.reasoner?.confidence_pct ??
    Math.round((data?.decision?.confidence ?? 0) * 100);
  const size = data?.decision?.size_pct ?? data?.risk?.adjusted_size_pct ?? 0;

  const metrics = [
    { label: "Action", value: `${action} ${token}`, accent: true },
    { label: "Size", value: `${size}%`, accent: false },
    { label: "Confidence", value: `${confidence}%`, accent: false },
  ];

  return (
    <PanelCard
      title="Agent Thought"
      subtitle={
        data?.perception?.reasoning_hash
          ? `hash ${data.perception.reasoning_hash}`
          : undefined
      }
      icon={<Brain className="h-4 w-4 text-accent" strokeWidth={1.75} />}
      className="lg:col-span-8"
      delay={0.05}
      glow
      headerRight={
        <div className="flex items-center gap-2">
          <Target className="h-3.5 w-3.5 text-muted" strokeWidth={1.5} />
          <div className="h-1.5 w-16 overflow-hidden rounded-full bg-border">
            <motion.div
              className="h-full rounded-full bg-accent"
              initial={{ width: 0 }}
              animate={{ width: `${confidence}%` }}
              transition={{ duration: 1, ease: [0.22, 1, 0.36, 1] }}
            />
          </div>
        </div>
      }
    >
      <blockquote className="relative pl-4">
        <span
          className="absolute left-0 top-0 font-display text-4xl leading-none text-accent/40"
          aria-hidden
        >
          &ldquo;
        </span>
        <p className="font-display text-lg leading-snug tracking-wide text-foreground sm:text-2xl md:text-[1.65rem]">
          {read}
        </p>
      </blockquote>
      {reasoning && (
        <p className="mt-5 max-w-3xl border-l border-border pl-4 font-mono text-sm leading-relaxed text-muted">
          {reasoning}
        </p>
      )}
      <div className="mt-8 grid grid-cols-1 gap-4 border-t border-border pt-6 sm:grid-cols-3 sm:gap-6">
        {metrics.map((metric, i) => (
          <motion.div
            key={metric.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 + i * 0.08 }}
            className="rounded border border-border/80 bg-background/40 px-4 py-3"
          >
            <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted">
              {metric.label}
            </div>
            <div
              className={`mt-1 font-mono text-xl ${metric.accent ? "text-accent" : "text-foreground"}`}
            >
              {metric.value}
            </div>
          </motion.div>
        ))}
      </div>
    </PanelCard>
  );
}