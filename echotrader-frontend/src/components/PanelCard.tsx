"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";

interface PanelCardProps {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
  children: ReactNode;
  className?: string;
  delay?: number;
  glow?: boolean;
  headerRight?: ReactNode;
}

export function PanelCard({
  title,
  subtitle,
  icon,
  children,
  className = "",
  delay = 0,
  glow = false,
  headerRight,
}: PanelCardProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55, delay, ease: [0.22, 1, 0.36, 1] }}
      className={`panel-card ${glow ? "panel-card-glow" : ""} ${className}`}
    >
      <div className="panel-inner-glow pointer-events-none absolute inset-0" />
      <div className="relative p-5 sm:p-6 md:p-7">
        <div className="mb-5 flex items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            {icon && (
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded border border-border bg-background/60">
                {icon}
              </div>
            )}
            <div>
              <h2 className="font-mono text-[11px] uppercase tracking-[0.22em] text-muted">
                {title}
              </h2>
              {subtitle && (
                <p className="mt-0.5 font-mono text-[10px] text-muted/80">{subtitle}</p>
              )}
            </div>
          </div>
          {headerRight}
        </div>
        {children}
      </div>
    </motion.section>
  );
}