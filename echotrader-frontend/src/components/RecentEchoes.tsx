"use client";

import { motion } from "framer-motion";
import { Waves } from "lucide-react";
import { PanelCard } from "@/components/PanelCard";
import type { EchoRecord } from "@/lib/types";

interface RecentEchoesProps {
  echoes: EchoRecord[];
}

const actionStyles: Record<string, string> = {
  buy: "text-[#c8f135] border-[#c8f135]/30",
  sell: "text-[#e23636] border-[#e23636]/30",
  hold: "text-accent border-accent/30",
};

export function RecentEchoes({ echoes }: RecentEchoesProps) {
  return (
    <PanelCard
      title="Recent Echoes"
      subtitle="Agent memory snapshots"
      icon={<Waves className="h-4 w-4 text-accent" strokeWidth={1.75} />}
      className="lg:col-span-7"
      delay={0.26}
    >
      <div className="space-y-3">
        {echoes.length === 0 && (
          <p className="rounded border border-dashed border-border py-8 text-center font-mono text-sm text-muted">
            No echoes recorded yet. Run a refresh cycle to capture the first snapshot.
          </p>
        )}
        {echoes.map((echo, i) => (
          <motion.div
            key={echo.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05 }}
            className="echo-timeline relative grid gap-3 rounded border border-border/80 bg-background/30 py-4 pl-5 pr-4 md:grid-cols-[130px_1fr_auto] md:gap-4"
          >
            <div className="font-mono text-[11px] leading-relaxed text-muted">
              {new Date(echo.timestamp).toLocaleString()}
            </div>
            <div>
              <div className="font-display text-sm leading-snug text-foreground">
                {echo.thesis}
              </div>
              <div className="mt-1.5 font-mono text-[10px] text-muted">
                {echo.snapshot_summary}
              </div>
            </div>
            <div
              className={`self-start rounded border px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.12em] ${
                actionStyles[echo.action.toLowerCase()] ?? actionStyles.hold
              }`}
            >
              {echo.action} · {Math.round(echo.confidence * 100)}%
            </div>
          </motion.div>
        ))}
      </div>
    </PanelCard>
  );
}