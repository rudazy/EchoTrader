import { Activity, Shield } from "lucide-react";

interface DashboardNavProps {
  online: boolean;
  dryRun: boolean;
  chain: string;
}

export function DashboardNav({ online, dryRun, chain }: DashboardNavProps) {
  return (
    <nav className="sticky top-0 z-50 border-b border-[#1f1f1f] bg-[#0a0a0a]/90 backdrop-blur-md">
      <div className="mx-auto flex max-w-[1200px] flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 sm:py-5 md:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded border border-[#333] bg-[#111111]">
            <Activity className="h-4 w-4 text-[#ff8a3d]" strokeWidth={1.75} />
          </div>
          <span className="font-sans text-xl font-medium tracking-wide text-[#f5f5f5]">
            EchoTrader
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-3 font-mono text-[10px] uppercase tracking-[0.14em] sm:gap-6 sm:text-xs">
          <div className="flex items-center gap-2 text-[#f5f5f5]">
            <span
              className={`h-2 w-2 rounded-full ${online ? "bg-[#ff8a3d] animate-pulse" : "bg-[#666]"}`}
            />
            {online ? "Agent Online" : "Agent Offline"}
          </div>
          <div className="hidden items-center gap-2 text-[#666666] sm:flex">
            <Shield className="h-3.5 w-3.5" />
            {chain} · Self-Custody
          </div>
          <div
            className={`rounded border px-2 py-1 ${
              dryRun
                ? "border-[#333] text-[#666666]"
                : "border-[#ff8a3d]/40 text-[#ff8a3d]"
            }`}
          >
            {dryRun ? "Dry Run" : "Live"}
          </div>
        </div>
      </div>
    </nav>
  );
}