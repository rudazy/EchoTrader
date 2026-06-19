import type { SVGProps } from "react";

interface LogoMarkProps extends SVGProps<SVGSVGElement> {
  size?: number;
}

/** Echo mirror mark — same geometry as public/icon.svg and public/og.svg */
export function LogoMark({ size = 32, className, ...props }: LogoMarkProps) {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 32 32"
      width={size}
      height={size}
      fill="none"
      aria-hidden
      className={className}
      {...props}
    >
      <path
        d="M8 16c0-4.4 3.6-8 8-8"
        stroke="#ff8a3d"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M24 16c0 4.4-3.6 8-8 8"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        opacity="0.85"
        className="text-foreground"
      />
      <circle cx="16" cy="16" r="2" fill="#ff8a3d" />
    </svg>
  );
}

interface LogoProps {
  showWordmark?: boolean;
  markSize?: number;
  online?: boolean;
  className?: string;
}

export function Logo({
  showWordmark = true,
  markSize = 36,
  online = false,
  className = "",
}: LogoProps) {
  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div
        className="relative flex shrink-0 items-center justify-center rounded border border-border bg-surface"
        style={{ width: markSize, height: markSize }}
      >
        {online && (
          <span
            className="absolute inset-0 rounded border border-accent/30"
            style={{ animation: "pulse-ring 2s ease-out infinite" }}
          />
        )}
        <LogoMark size={markSize - 14} className="relative" />
      </div>
      {showWordmark && (
        <div>
          <span className="font-display text-xl font-medium tracking-wide text-foreground">
            EchoTrader
          </span>
          <div className="font-mono text-[9px] uppercase tracking-[0.2em] text-muted">
            Market Mirror v0.1
          </div>
        </div>
      )}
    </div>
  );
}