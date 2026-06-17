import { Activity, Shield } from "lucide-react";
import { ThemeToggle } from "@/components/ThemeToggle";

interface DashboardNavProps {
  online: boolean;
  dryRun: boolean;
  chain: string;
}

export function DashboardNav({ online, dryRun, chain }: DashboardNavProps) {
  return (
    <nav
      className="sticky top-0 z-50 border-b border-border backdrop-blur-md transition-colors duration-400"
      style={{ backgroundColor: "var(--nav-bg)" }}
    >
      <div className="mx-auto flex max-w-[1200px] flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 sm:py-5 md:px-8">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded border border-border bg-surface">
            <Activity className="h-4 w-4 text-accent" strokeWidth={1.75} />
          </div>
          <span className="font-display text-xl font-medium tracking-wide text-foreground">
            EchoTrader
          </span>
        </div>
        <div className="flex flex-wrap items-center gap-3 font-mono text-[10px] uppercase tracking-[0.14em] sm:gap-4 sm:text-xs">
          <div className="flex items-center gap-2 text-foreground">
            <span
              className={`h-2 w-2 rounded-full ${online ? "animate-pulse bg-accent" : "bg-muted"}`}
            />
            {online ? "Agent Online" : "Agent Offline"}
          </div>
          <div className="hidden items-center gap-2 text-muted sm:flex">
            <Shield className="h-3.5 w-3.5" />
            {chain} · Self-Custody
          </div>
          <div
            className={`rounded border px-2 py-1 ${
              dryRun ? "border-border text-muted" : "border-accent/40 text-accent"
            }`}
          >
            {dryRun ? "Dry Run" : "Live"}
          </div>
          <ThemeToggle />
        </div>
      </div>
    </nav>
  );
}