import type { DashboardStatus } from "@/lib/types";

interface LiveSignalsProps {
  data: DashboardStatus | null;
}

function SignalRow({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="border-b border-border pb-4 last:border-0 last:pb-0">
      <div className="font-mono text-3xl text-foreground">{value}</div>
      <div className="mt-1 font-mono text-xs uppercase tracking-[0.14em] text-muted">
        {label}
      </div>
      {sub && <div className="mt-1 font-mono text-[11px] text-muted">{sub}</div>}
    </div>
  );
}

export function LiveSignals({ data }: LiveSignalsProps) {
  const signals = data?.signals;
  const fg = signals?.fear_greed ?? "—";
  const divergence = signals?.divergence_score ?? "neutral";
  const btcDom = signals?.btc_dominance?.toFixed(1) ?? "—";
  const social = signals?.social_heat?.toFixed(2) ?? "—";
  const flow = signals?.onchain_flow ?? "—";

  return (
    <section className="fade-up fade-up-delay surface-card flex flex-col p-5 sm:p-8 lg:col-span-4">
      <div className="mb-6 font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
        Live Signals
      </div>
      <div className="space-y-5">
        <SignalRow
          label="Fear & Greed"
          value={String(fg)}
          sub={signals?.fear_greed_label ?? undefined}
        />
        <SignalRow label="Divergence" value={divergence.replaceAll("_", " ")} />
        <SignalRow label="BTC Dominance" value={`${btcDom}%`} />
        <SignalRow label="Social Heat" value={String(social)} />
        <SignalRow label="On-Chain Flow" value={flow.replaceAll("_", " ")} />
      </div>
    </section>
  );
}