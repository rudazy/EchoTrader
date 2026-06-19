"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useCallback, useEffect, useState } from "react";
import { AgentThought } from "@/components/AgentThought";
import { DashboardNav } from "@/components/DashboardNav";
import { HeroSection } from "@/components/HeroSection";
import { HistoryChart } from "@/components/HistoryChart";
import { LiveSignals } from "@/components/LiveSignals";
import { MarketTicker } from "@/components/MarketTicker";
import { PortfolioPanel } from "@/components/PortfolioPanel";
import { RecentEchoes } from "@/components/RecentEchoes";
import {
  AgentThoughtSkeleton,
  ChartSkeleton,
  PanelSkeleton,
  SignalsSkeleton,
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
      if (refresh) setRefreshing(true);
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
    <div className="min-h-screen text-foreground transition-colors duration-400">
      <DashboardNav
        online={data?.agent_online ?? !loading}
        dryRun={data?.dry_run ?? true}
        chain={data?.chain ?? "BNB"}
      />

      <main className="mx-auto max-w-[1200px] px-4 py-8 sm:px-6 sm:py-10 md:px-8 md:py-12">
        <HeroSection
          data={data}
          loading={loading}
          refreshing={refreshing}
          onRefresh={() => load(true)}
        />

        {!showSkeleton && <MarketTicker data={data} />}

        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="panel-card mb-6 overflow-hidden"
            >
              <div className="px-4 py-3 font-mono text-xs text-muted sm:text-sm">
                API unreachable ({error}). Start backend:{" "}
                <code className="text-accent">python -m api.server</code>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <motion.div
          layout
          className={`grid grid-cols-1 gap-5 sm:gap-6 lg:grid-cols-12 ${
            refreshing ? "opacity-75 transition-opacity duration-300" : ""
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
        </motion.div>
      </main>
    </div>
  );
}