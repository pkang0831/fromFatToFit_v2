'use client';

export function SkeletonStats({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-24 rounded-2xl bg-surfaceAlt dark:bg-white/[0.04] skeleton-shimmer" />
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="h-64 rounded-2xl bg-surfaceAlt dark:bg-white/[0.04] skeleton-shimmer" />
  );
}

export function SkeletonCard() {
  return (
    <div className="h-32 rounded-2xl bg-surfaceAlt dark:bg-white/[0.04] skeleton-shimmer" />
  );
}

export function SkeletonList({ items = 4 }: { items?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="h-14 rounded-xl bg-surfaceAlt dark:bg-white/[0.04] skeleton-shimmer" />
      ))}
    </div>
  );
}
