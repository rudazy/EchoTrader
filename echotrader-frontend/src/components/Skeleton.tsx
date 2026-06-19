interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className = "" }: SkeletonProps) {
  return (
    <div
      className={`skeleton-shimmer rounded ${className}`}
      aria-hidden
    />
  );
}

export function AgentThoughtSkeleton() {
  return (
    <section className="panel-card p-5 sm:p-8 lg:col-span-8">
      <Skeleton className="mb-6 h-3 w-28" />
      <Skeleton className="mb-3 h-8 w-full" />
      <Skeleton className="mb-3 h-8 w-11/12" />
      <Skeleton className="h-4 w-2/3" />
      <div className="mt-8 grid grid-cols-1 gap-4 border-t border-border pt-6 sm:grid-cols-3 sm:gap-6">
        <Skeleton className="h-14 w-full" />
        <Skeleton className="h-14 w-full" />
        <Skeleton className="h-14 w-full" />
      </div>
    </section>
  );
}

export function SignalsSkeleton() {
  return (
    <section className="panel-card p-5 sm:p-8 lg:col-span-4">
      <Skeleton className="mb-6 h-3 w-24" />
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="rounded border border-border/50 p-3">
            <Skeleton className="mb-2 h-8 w-16" />
            <Skeleton className="mb-2 h-3 w-24" />
            <Skeleton className="h-1 w-full" />
          </div>
        ))}
      </div>
    </section>
  );
}

export function ChartSkeleton() {
  return (
    <section className="panel-card p-4 sm:p-6 lg:col-span-5">
      <Skeleton className="mb-4 h-3 w-36" />
      <Skeleton className="h-52 w-full sm:h-64" />
    </section>
  );
}

export function PanelSkeleton({ span = 4 }: { span?: 4 | 7 | 12 }) {
  const spanClass =
    span === 12 ? "lg:col-span-12" : span === 7 ? "lg:col-span-7" : "lg:col-span-4";
  return (
    <section className={`panel-card p-5 sm:p-6 ${spanClass}`}>
      <Skeleton className="mb-4 h-3 w-24" />
      <Skeleton className="mb-3 h-16 w-full" />
      <Skeleton className="mb-3 h-16 w-full" />
      <Skeleton className="h-16 w-full" />
    </section>
  );
}