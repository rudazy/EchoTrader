"use client";

import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { PerceptionHistoryEntry } from "@/lib/types";

interface HistoryChartProps {
  history: PerceptionHistoryEntry[];
  currentFg?: number | null;
}

export function HistoryChart({ history, currentFg }: HistoryChartProps) {
  const source = history.length > 0 ? history.slice(-12) : [];
  const data =
    source.length > 0
      ? source.map((echo) => ({
          time: new Date(echo.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          }),
          fg: echo.fear_greed_index ?? 50,
        }))
      : [{ time: "Now", fg: currentFg ?? 50 }];

  return (
    <section className="rounded border border-[#1f1f1f] bg-[#111111] p-4 sm:p-6 lg:col-span-5">
      <div className="mb-4 font-mono text-[11px] uppercase tracking-[0.2em] text-[#666666]">
        Fear &amp; Greed History
      </div>
      <div className="mt-2 h-52 w-full sm:h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
            <XAxis
              dataKey="time"
              stroke="#1f1f1f"
              tick={{ fill: "#666666", fontSize: 10, fontFamily: "var(--font-geist-mono)" }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[0, 100]}
              stroke="#1f1f1f"
              tick={{ fill: "#666666", fontSize: 10, fontFamily: "var(--font-geist-mono)" }}
              tickLine={false}
              width={32}
            />
            <Tooltip
              contentStyle={{
                background: "#111111",
                border: "1px solid #1f1f1f",
                borderRadius: 4,
                fontFamily: "var(--font-geist-mono)",
                fontSize: 12,
              }}
              labelStyle={{ color: "#666666" }}
              formatter={(value) => [`${value}`, "Fear & Greed"]}
            />
            <Line
              type="natural"
              dataKey="fg"
              stroke="#ff8a3d"
              strokeWidth={2.5}
              dot={{ fill: "#ff8a3d", r: 3 }}
              activeDot={{ r: 5, fill: "#ff8a3d" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-2 text-center font-mono text-[10px] uppercase tracking-[0.12em] text-[#666666]">
        Last {data.length} perception echoes
      </p>
    </section>
  );
}