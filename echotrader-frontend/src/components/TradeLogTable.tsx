import type { TradeRecord } from "@/lib/types";

interface TradeLogTableProps {
  trades: TradeRecord[];
}

export function TradeLogTable({ trades }: TradeLogTableProps) {
  return (
    <section className="surface-card p-4 sm:p-6 lg:col-span-12">
      <div className="mb-4 font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
        Execution Log
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse font-mono text-xs">
          <thead>
            <tr className="border-b border-border text-left text-muted">
              <th className="pb-3 pr-4 font-normal uppercase tracking-[0.12em]">Time</th>
              <th className="pb-3 pr-4 font-normal uppercase tracking-[0.12em]">Action</th>
              <th className="pb-3 pr-4 font-normal uppercase tracking-[0.12em]">Status</th>
              <th className="pb-3 pr-4 font-normal uppercase tracking-[0.12em]">Quote</th>
              <th className="pb-3 font-normal uppercase tracking-[0.12em]">Hash</th>
            </tr>
          </thead>
          <tbody>
            {trades.length === 0 && (
              <tr>
                <td colSpan={5} className="py-6 text-muted">
                  No trades logged yet.
                </td>
              </tr>
            )}
            {trades.map((trade, index) => (
              <tr key={`${trade.timestamp}-${index}`} className="border-b border-border/70">
                <td className="py-3 pr-4 text-muted">
                  {new Date(trade.timestamp).toLocaleString()}
                </td>
                <td className="py-3 pr-4 text-foreground">
                  {trade.action.toUpperCase()} {trade.token}
                </td>
                <td className="py-3 pr-4 text-foreground">
                  {trade.status}
                  {trade.dry_run ? " (dry)" : ""}
                </td>
                <td className="py-3 pr-4 text-muted">{trade.quote_summary ?? "—"}</td>
                <td className="py-3 text-muted">
                  {trade.tx_hash ?? trade.reasoning_hash ?? "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}