import type { DashboardStatus } from "@/lib/types";

interface PortfolioPanelProps {
  data: DashboardStatus | null;
}

export function PortfolioPanel({ data }: PortfolioPanelProps) {
  const portfolio = data?.portfolio;
  const risk = data?.risk;

  return (
    <section className="surface-card p-4 sm:p-6 lg:col-span-4">
      <div className="mb-4 font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
        Portfolio
      </div>
      <div className="space-y-5 font-mono text-sm">
        <div>
          <div className="text-muted">Allocated Capital</div>
          <div className="mt-1 text-2xl text-foreground">
            ${portfolio?.allocated_capital_usd?.toLocaleString() ?? "—"}
          </div>
        </div>
        <div>
          <div className="text-muted">Deployed</div>
          <div className="mt-1 text-xl text-foreground">{portfolio?.deployed_pct ?? 0}%</div>
        </div>
        <div>
          <div className="text-muted">Primary Token</div>
          <div className="mt-1 text-xl text-accent">{portfolio?.token ?? "—"}</div>
        </div>
        <div className="border-t border-border pt-4">
          <div className="text-muted">Risk Gate</div>
          <div className="mt-1 text-foreground">
            {risk?.approved ? "Approved" : "Blocked"}
          </div>
          {risk?.reasons?.[0] && (
            <div className="mt-1 text-[11px] text-muted">{risk.reasons[0]}</div>
          )}
        </div>
      </div>
    </section>
  );
}