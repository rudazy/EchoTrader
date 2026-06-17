import type { DashboardStatus } from "@/lib/types";

interface PortfolioPanelProps {
  data: DashboardStatus | null;
}

export function PortfolioPanel({ data }: PortfolioPanelProps) {
  const portfolio = data?.portfolio;
  const risk = data?.risk;

  return (
    <section className="rounded border border-[#1f1f1f] bg-[#111111] p-6 lg:col-span-4">
      <div className="mb-4 font-mono text-[11px] uppercase tracking-[0.2em] text-[#666666]">
        Portfolio
      </div>
      <div className="space-y-5 font-mono text-sm">
        <div>
          <div className="text-[#666666]">Allocated Capital</div>
          <div className="mt-1 text-2xl text-[#f5f5f5]">
            ${portfolio?.allocated_capital_usd?.toLocaleString() ?? "—"}
          </div>
        </div>
        <div>
          <div className="text-[#666666]">Deployed</div>
          <div className="mt-1 text-xl text-[#f5f5f5]">{portfolio?.deployed_pct ?? 0}%</div>
        </div>
        <div>
          <div className="text-[#666666]">Primary Token</div>
          <div className="mt-1 text-xl text-[#ff8a3d]">{portfolio?.token ?? "—"}</div>
        </div>
        <div className="border-t border-[#1f1f1f] pt-4">
          <div className="text-[#666666]">Risk Gate</div>
          <div className="mt-1 text-[#f5f5f5]">
            {risk?.approved ? "Approved" : "Blocked"}
          </div>
          {risk?.reasons?.[0] && (
            <div className="mt-1 text-[11px] text-[#666666]">{risk.reasons[0]}</div>
          )}
        </div>
      </div>
    </section>
  );
}