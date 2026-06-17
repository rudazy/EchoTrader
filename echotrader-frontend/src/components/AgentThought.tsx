import type { DashboardStatus } from "@/lib/types";

interface AgentThoughtProps {
  data: DashboardStatus | null;
}

export function AgentThought({ data }: AgentThoughtProps) {
  const read =
    data?.reasoner?.market_read ??
    "Waiting for agent perception cycle. Signals will appear here.";
  const reasoning = data?.reasoner?.reasoning ?? data?.reasoner?.risk_notes ?? "";
  const action = (data?.decision?.action ?? "hold").toUpperCase();
  const token = data?.decision?.token ?? "—";
  const confidence =
    data?.reasoner?.confidence_pct ??
    Math.round((data?.decision?.confidence ?? 0) * 100);
  const size = data?.decision?.size_pct ?? data?.risk?.adjusted_size_pct ?? 0;

  return (
    <section className="fade-up relative overflow-hidden rounded border border-[#1f1f1f] bg-[#111111] p-5 sm:p-8 lg:col-span-8">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_20%_0%,rgba(255,138,61,0.08),transparent_45%)]" />
      <div className="relative">
        <div className="mb-6 flex items-center gap-3">
          <span className="font-mono text-[11px] uppercase tracking-[0.2em] text-[#666666]">
            Agent Thought
          </span>
          {data?.perception?.reasoning_hash && (
            <span className="font-mono text-[10px] text-[#666666]">
              hash {data.perception.reasoning_hash}
            </span>
          )}
        </div>
        <p className="font-sans text-lg leading-snug tracking-wide text-[#f5f5f5] sm:text-2xl md:text-[1.65rem]">
          &ldquo;{read}&rdquo;
        </p>
        {reasoning && (
          <p className="mt-5 max-w-3xl font-mono text-sm leading-relaxed text-[#666666]">
            {reasoning}
          </p>
        )}
        <div className="mt-8 grid grid-cols-1 gap-4 border-t border-[#1f1f1f] pt-6 sm:grid-cols-3 sm:gap-6">
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-[#666666]">
              Action
            </div>
            <div className="mt-1 font-mono text-xl text-[#ff8a3d]">
              {action} {token}
            </div>
          </div>
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-[#666666]">
              Size
            </div>
            <div className="mt-1 font-mono text-xl text-[#f5f5f5]">{size}%</div>
          </div>
          <div>
            <div className="font-mono text-[10px] uppercase tracking-[0.16em] text-[#666666]">
              Confidence
            </div>
            <div className="mt-1 font-mono text-xl text-[#f5f5f5]">{confidence}%</div>
          </div>
        </div>
      </div>
    </section>
  );
}