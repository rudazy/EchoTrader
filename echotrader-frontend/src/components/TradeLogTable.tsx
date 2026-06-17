import type { TradeRecord } from "@/lib/types";

interface TradeLogTableProps {
  trades: TradeRecord[];
}

export function TradeLogTable({ trades }: TradeLogTableProps) {
  return (
    <section className="rounded border border-[#1f1f1f] bg-[#111111] p-4 sm:p-6 lg:col-span-12">
      <div className="mb-4 font-mono text-[11px] uppercase tracking-[0.2em] text-[#666666]">
        Execution Log
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse font-mono text-xs">
          <thead>
            <tr className="border-b border-[#1f1f1f] text-left text-[#666666]">
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
                <td colSpan={5} className="py-6 text-[#666666]">
                  No trades logged yet.
                </td>
              </tr>
            )}
            {trades.map((trade, index) => (
              <tr key={`${trade.timestamp}-${index}`} className="border-b border-[#1f1f1f]/70">
                <td className="py-3 pr-4 text-[#666666]">
                  {new Date(trade.timestamp).toLocaleString()}
                </td>
                <td className="py-3 pr-4 text-[#f5f5f5]">
                  {trade.action.toUpperCase()} {trade.token}
                </td>
                <td className="py-3 pr-4 text-[#f5f5f5]">
                  {trade.status}
                  {trade.dry_run ? " (dry)" : ""}
                </td>
                <td className="py-3 pr-4 text-[#666666]">{trade.quote_summary ?? "—"}</td>
                <td className="py-3 text-[#666666]">
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