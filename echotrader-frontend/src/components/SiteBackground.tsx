export function SiteBackground() {
  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 -z-10 overflow-hidden"
    >
      <div className="absolute inset-0 bg-background transition-colors duration-500" />
      <div
        className="bg-grid absolute inset-0 transition-opacity duration-500"
        style={{ opacity: "var(--grid-opacity)" }}
      />
      <div className="contour-lines absolute inset-0 opacity-60" />
      <div
        className="animate-float-orb absolute -left-32 top-1/4 h-[420px] w-[420px] rounded-full blur-[100px]"
        style={{ background: "var(--orb-1)" }}
      />
      <div
        className="animate-float-orb-delay absolute -right-24 bottom-1/4 h-[360px] w-[360px] rounded-full blur-[90px]"
        style={{ background: "var(--orb-2)" }}
      />
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(ellipse 80% 50% at 50% -10%, var(--glow), transparent 65%)",
        }}
      />
      <div
        className="absolute inset-0"
        style={{
          opacity: "var(--grain-opacity)",
          backgroundImage:
            "url(\"data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")",
        }}
      />
    </div>
  );
}