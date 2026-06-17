"use client";

import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useTheme } from "@/components/ThemeProvider";
import type { PerceptionHistoryEntry } from "@/lib/types";

interface HistoryChartProps {
  history: PerceptionHistoryEntry[];
  currentFg?: number | null;
}

export function HistoryChart({ history, currentFg }: HistoryChartProps) {
  const { theme } = useTheme();
  const tickColor = theme === "light" ? "#5c5c5c" : "#666666";
  const axisColor = theme === "light" ? "#e5e5e5" : "#1f1f1f";
  const tooltipBg = theme === "light" ? "#ffffff" : "#111111";
  const accent = theme === "light" ? "#e86b1f" : "#ff8a3d";

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
    <section className="surface-card p-4 sm:p-6 lg:col-span-5">
      <div className="mb-4 font-mono text-[11px] uppercase tracking-[0.2em] text-muted">
        Fear &amp; Greed History
      </div>
      <div className="mt-2 h-52 w-full sm:h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
            <XAxis
              dataKey="time"
              stroke={axisColor}
              tick={{ fill: tickColor, fontSize: 10, fontFamily: "var(--font-geist-mono)" }}
              tickLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[0, 100]}
              stroke={axisColor}
              tick={{ fill: tickColor, fontSize: 10, fontFamily: "var(--font-geist-mono)" }}
              tickLine={false}
              width={32}
            />
            <Tooltip
              contentStyle={{
                background: tooltipBg,
                border: `1px solid ${axisColor}`,
                borderRadius: 4,
                fontFamily: "var(--font-geist-mono)",
                fontSize: 12,
                color: tickColor,
              }}
              labelStyle={{ color: tickColor }}
              formatter={(value) => [`${value}`, "Fear & Greed"]}
            />
            <Line
              type="natural"
              dataKey="fg"
              stroke={accent}
              strokeWidth={2.5}
              dot={{ fill: accent, r: 3 }}
              activeDot={{ r: 5, fill: accent }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-2 text-center font-mono text-[10px] uppercase tracking-[0.12em] text-muted">
        Last {data.length} perception echoes
      </p>
    </section>
  );
}