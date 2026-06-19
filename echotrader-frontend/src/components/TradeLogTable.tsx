"use client";

import { motion } from "framer-motion";
import { ScrollText } from "lucide-react";
import { PanelCard } from "@/components/PanelCard";
import type { TradeRecord } from "@/lib/types";

interface TradeLogTableProps {
  trades: TradeRecord[];
}

export function TradeLogTable({ trades }: TradeLogTableProps) {
  return (
    <PanelCard
      title="Execution Log"
      subtitle="On-chain and dry-run history"
      icon={<ScrollText className="h-4 w-4 text-accent" strokeWidth={1.75} />}
      className="lg:col-span-12"
      delay={0.3}
    >
      <div className="overflow-x-auto rounded border border-border/60">
        <table className="w-full min-w-[720px] border-collapse font-mono text-xs">
          <thead>
            <tr className="border-b border-border bg-background/50 text-left text-muted">
              <th className="px-4 py-3 font-normal uppercase tracking-[0.12em]">Time</th>
              <th className="px-4 py-3 font-normal uppercase tracking-[0.12em]">Action</th>
              <th className="px-4 py-3 font-normal uppercase tracking-[0.12em]">Status</th>
              <th className="px-4 py-3 font-normal uppercase tracking-[0.12em]">Quote</th>
              <th className="px-4 py-3 font-normal uppercase tracking-[0.12em]">Hash</th>
            </tr>
          </thead>
          <tbody>
            {trades.length === 0 && (
              <tr>
                <td colSpan={5} className="px-4 py-10 text-center text-muted">
                  No trades logged yet. Agent is observing.
                </td>
              </tr>
            )}
            {trades.map((trade, index) => (
              <motion.tr
                key={`${trade.timestamp}-${index}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: index * 0.04 }}
                className="border-b border-border/50 transition hover:bg-background/40"
              >
                <td className="px-4 py-3.5 text-muted">
                  {new Date(trade.timestamp).toLocaleString()}
                </td>
                <td className="px-4 py-3.5 font-medium text-foreground">
                  {trade.action.toUpperCase()} {trade.token}
                </td>
                <td className="px-4 py-3.5 text-foreground">
                  <span
                    className={`rounded border px-2 py-0.5 text-[10px] uppercase tracking-[0.08em] ${
                      trade.dry_run
                        ? "border-border text-muted"
                        : "border-accent/40 text-accent"
                    }`}
                  >
                    {trade.status}
                    {trade.dry_run ? " (dry)" : ""}
                  </span>
                </td>
                <td className="px-4 py-3.5 text-muted">{trade.quote_summary ?? "—"}</td>
                <td className="max-w-[180px] truncate px-4 py-3.5 text-muted">
                  {trade.tx_hash ?? trade.reasoning_hash ?? "—"}
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </PanelCard>
  );
}