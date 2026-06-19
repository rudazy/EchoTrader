"use client";

import { motion } from "framer-motion";
import { Shield } from "lucide-react";
import { Logo } from "@/components/Logo";
import { ThemeToggle } from "@/components/ThemeToggle";

interface DashboardNavProps {
  online: boolean;
  dryRun: boolean;
  chain: string;
}

export function DashboardNav({ online, dryRun, chain }: DashboardNavProps) {
  return (
    <motion.nav
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45 }}
      className="sticky top-0 z-50 border-b border-border backdrop-blur-md transition-colors duration-400"
      style={{ backgroundColor: "var(--nav-bg)" }}
    >
      <div className="mx-auto flex max-w-[1200px] flex-col gap-4 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6 sm:py-4 md:px-8">
        <Logo online={online} />
        <div className="flex flex-wrap items-center gap-3 font-mono text-[10px] uppercase tracking-[0.14em] sm:gap-4 sm:text-xs">
          <div className="stat-pill flex items-center gap-2 rounded px-3 py-1.5 text-foreground">
            <span
              className={`relative h-2 w-2 rounded-full ${online ? "bg-accent" : "bg-muted"}`}
            >
              {online && (
                <span className="absolute inset-0 animate-ping rounded-full bg-accent opacity-60" />
              )}
            </span>
            {online ? "Agent Online" : "Agent Offline"}
          </div>
          <div className="hidden items-center gap-2 text-muted sm:flex">
            <Shield className="h-3.5 w-3.5 text-accent/80" />
            {chain} · Self-Custody
          </div>
          <div
            className={`stat-pill rounded px-3 py-1.5 ${
              dryRun ? "text-muted" : "border-accent/40 text-accent"
            }`}
          >
            {dryRun ? "Dry Run" : "Live"}
          </div>
          <ThemeToggle />
        </div>
      </div>
    </motion.nav>
  );
}