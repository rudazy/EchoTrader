import type { EchoRecord } from "@/lib/types";

interface RecentEchoesProps {
  echoes: EchoRecord[];
}

export function RecentEchoes({ echoes }: RecentEchoesProps) {
  return (
    <section className="surface-card p-4 sm:p-6 lg:col-span-7">
      <div className="mb-4 font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
        Recent Echoes
      </div>
      <div className="space-y-3">
        {echoes.length === 0 && (
          <p className="font-mono text-sm text-muted">No echoes recorded yet.</p>
        )}
        {echoes.map((echo) => (
          <div
            key={echo.id}
            className="grid gap-2 border border-border bg-background p-4 md:grid-cols-[120px_1fr_auto]"
          >
            <div className="font-mono text-[11px] text-muted">
              {new Date(echo.timestamp).toLocaleString()}
            </div>
            <div>
              <div className="font-display text-sm text-foreground">{echo.thesis}</div>
              <div className="mt-1 font-mono text-[11px] text-muted">
                {echo.snapshot_summary}
              </div>
            </div>
            <div className="font-mono text-xs uppercase tracking-[0.12em] text-accent">
              {echo.action} · {Math.round(echo.confidence * 100)}%
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}