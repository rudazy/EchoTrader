"use client";

import {
  Area,
  AreaChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { TrendingDown } from "lucide-react";
import { useTheme } from "@/components/ThemeProvider";
import { PanelCard } from "@/components/PanelCard";
import type { PerceptionHistoryEntry } from "@/lib/types";

interface HistoryChartProps {
  history: PerceptionHistoryEntry[];
  currentFg?: number | null;
}

export function HistoryChart({ history, currentFg }: HistoryChartProps) {
  const { theme } = useTheme();
  const tickColor = theme === "light" ? "#5c5c5c" : "#666666";
  const axisColor = theme === "light" ? "#e5e5e5" : "#1f1f1f";
  const tooltipBg = theme === "light" ? "#ffffff" : "#141414";
  const accent = theme === "light" ? "#e86b1f" : "#ff8a3d";
  const accentSoft = theme === "light" ? "rgba(232,107,31,0.15)" : "rgba(255,138,61,0.12)";

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
    <PanelCard
      title="Fear & Greed History"
      subtitle={`Last ${data.length} perception echoes`}
      icon={<TrendingDown className="h-4 w-4 text-accent" strokeWidth={1.75} />}
      className="lg:col-span-5"
      delay={0.18}
    >
      <div className="h-52 w-full sm:h-64">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
            <defs>
              <linearGradient id="fgGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={accent} stopOpacity={0.35} />
                <stop offset="100%" stopColor={accent} stopOpacity={0} />
              </linearGradient>
            </defs>
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
                boxShadow: "0 8px 24px -8px rgba(0,0,0,0.4)",
              }}
              labelStyle={{ color: tickColor }}
              formatter={(value) => [`${value}`, "Fear & Greed"]}
            />
            <Area
              type="monotone"
              dataKey="fg"
              stroke="none"
              fill="url(#fgGradient)"
            />
            <Line
              type="natural"
              dataKey="fg"
              stroke={accent}
              strokeWidth={2.5}
              dot={{ fill: accent, r: 3, strokeWidth: 0 }}
              activeDot={{ r: 6, fill: accent, stroke: accentSoft, strokeWidth: 8 }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </PanelCard>
  );
}