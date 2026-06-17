"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "@/components/ThemeProvider";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={theme === "dark" ? "Switch to light theme" : "Switch to dark theme"}
      className="flex items-center gap-2 rounded border border-border bg-surface px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.12em] text-muted transition hover:border-accent/40 hover:text-foreground sm:text-xs"
    >
      {theme === "dark" ? (
        <>
          <Sun className="h-3.5 w-3.5 text-accent" strokeWidth={1.75} />
          Light
        </>
      ) : (
        <>
          <Moon className="h-3.5 w-3.5 text-accent" strokeWidth={1.75} />
          Dark
        </>
      )}
    </button>
  );
}