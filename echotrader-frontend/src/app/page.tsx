"use client";

import { useCallback, useEffect, useState } from "react";
import { AgentThought } from "@/components/AgentThought";
import { DashboardNav } from "@/components/DashboardNav";
import { HistoryChart } from "@/components/HistoryChart";
import { LiveSignals } from "@/components/LiveSignals";
import { PortfolioPanel } from "@/components/PortfolioPanel";
import { RecentEchoes } from "@/components/RecentEchoes";
import {
  AgentThoughtSkeleton,
  ChartSkeleton,
  PanelSkeleton,
  SignalsSkeleton,
  Skeleton,
} from "@/components/Skeleton";
import { TradeLogTable } from "@/components/TradeLogTable";
import { fetchStatus } from "@/lib/api";
import type { DashboardStatus } from "@/lib/types";

export default function EchoTraderDashboard() {
  const [data, setData] = useState<DashboardStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async (refresh = false) => {
    try {
      if (refresh) {
        setRefreshing(true);
      }
      const status = await fetchStatus(refresh);
      setData(status);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load status");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    load(false);
    const interval = setInterval(() => load(false), 30000);
    return () => clearInterval(interval);
  }, [load]);

  const showSkeleton = loading && !data;

  return (
    <div className="min-h-screen text-[#f5f5f5]">
      <DashboardNav
        online={data?.agent_online ?? !loading}
        dryRun={data?.dry_run ?? true}
        chain={data?.chain ?? "BNB"}
      />

      <main className="mx-auto max-w-[1200px] px-4 py-8 sm:px-6 sm:py-10 md:px-8 md:py-12">
        <header className="mb-8 flex flex-col gap-5 sm:mb-10 sm:gap-6 md:flex-row md:items-end md:justify-between">
          <div>
            <h1 className="font-sans text-3xl font-medium tracking-wide text-[#f5f5f5] sm:text-4xl md:text-5xl">
              Market Mirror
            </h1>
            <p className="mt-2 font-mono text-xs text-[#666666] sm:text-sm md:text-base">
              Autonomous · Contrarian · Disciplined
            </p>
          </div>
          <div className="text-left md:text-right">
            <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-[#666666]">
              Current Regime
            </div>
            {showSkeleton ? (
              <Skeleton className="mt-2 h-8 w-40 md:ml-auto" />
            ) : (
              <div className="mt-1 font-mono text-xl text-[#ff8a3d] sm:text-2xl md:text-3xl">
                {data?.regime_label ?? "—"}
              </div>
            )}
            <button
              type="button"
              onClick={() => load(true)}
              disabled={refreshing || loading}
              className="mt-4 w-full rounded border border-[#333] px-3 py-2 font-mono text-[11px] uppercase tracking-[0.12em] text-[#666666] transition hover:border-[#ff8a3d]/50 hover:text-[#f5f5f5] disabled:opacity-50 sm:w-auto"
            >
              {refreshing ? "Refreshing..." : "Refresh Agent"}
            </button>
          </div>
        </header>

        {error && (
          <div className="mb-6 rounded border border-[#333] bg-[#111111] px-4 py-3 font-mono text-xs text-[#666666] sm:text-sm">
            API unreachable ({error}). Start backend:{" "}
            <code className="text-[#f5f5f5]">python -m api.server</code>
          </div>
        )}

        <div
          className={`grid grid-cols-1 gap-4 sm:gap-6 lg:grid-cols-12 ${
            refreshing ? "opacity-80 transition-opacity" : ""
          }`}
        >
          {showSkeleton ? (
            <>
              <AgentThoughtSkeleton />
              <SignalsSkeleton />
              <ChartSkeleton />
              <PanelSkeleton span={4} />
              <PanelSkeleton span={7} />
              <PanelSkeleton span={12} />
            </>
          ) : (
            <>
              <AgentThought data={data} />
              <LiveSignals data={data} />
              <HistoryChart
                history={data?.perception_history ?? []}
                currentFg={data?.signals.fear_greed}
              />
              <PortfolioPanel data={data} />
              <RecentEchoes echoes={data?.recent_echoes ?? []} />
              <TradeLogTable trades={data?.recent_trades ?? []} />
            </>
          )}
        </div>
      </main>
    </div>
  );
}