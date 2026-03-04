'use client';

export function SkeletonStats({ count = 4 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="h-24 rounded-xl bg-gray-200 dark:bg-gray-700 animate-pulse" />
      ))}
    </div>
  );
}

export function SkeletonChart() {
  return (
    <div className="h-64 rounded-xl bg-gray-200 dark:bg-gray-700 animate-pulse" />
  );
}

export function SkeletonCard() {
  return (
    <div className="h-32 rounded-xl bg-gray-200 dark:bg-gray-700 animate-pulse" />
  );
}

export function SkeletonList({ items = 4 }: { items?: number }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: items }).map((_, i) => (
        <div key={i} className="h-14 rounded-lg bg-gray-200 dark:bg-gray-700 animate-pulse" />
      ))}
    </div>
  );
}
