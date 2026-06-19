"use client";

import { motion } from "framer-motion";

interface FearGreedGaugeProps {
  value: number | null | undefined;
  label?: string | null;
  size?: number;
}

function gaugeColor(value: number): string {
  if (value <= 25) return "#e23636";
  if (value <= 45) return "#ff8a3d";
  if (value <= 55) return "#a8a8a8";
  if (value <= 75) return "#c8f135";
  return "#f5c842";
}

export function FearGreedGauge({ value, label, size = 140 }: FearGreedGaugeProps) {
  const v = value ?? 50;
  const stroke = gaugeColor(v);
  const radius = (size - 16) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (v / 100) * circumference;

  return (
    <div className="relative flex flex-col items-center">
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="var(--border)"
          strokeWidth={6}
        />
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={stroke}
          strokeWidth={6}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: [0.22, 1, 0.36, 1] }}
          style={{
            filter: `drop-shadow(0 0 8px color-mix(in srgb, ${stroke} 40%, transparent))`,
          }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.span
          key={v}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="font-display text-3xl font-medium text-foreground"
        >
          {value ?? "—"}
        </motion.span>
        {label && (
          <span className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.14em] text-muted">
            {label}
          </span>
        )}
      </div>
    </div>
  );
}