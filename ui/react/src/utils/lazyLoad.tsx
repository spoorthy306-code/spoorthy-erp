import { ComponentType, LazyExoticComponent, Suspense, lazy } from 'react';
import { LoadingSpinner } from '@/components/common/LoadingSpinner';

function RouteLoadingFallback() {
  return (
    <div className="flex min-h-[40vh] items-center justify-center" aria-live="polite">
      <div className="flex items-center gap-3 rounded-full border border-slate-200 bg-white px-4 py-3 text-sm text-slate-600 shadow-sm">
        <LoadingSpinner />
        <span>Loading workspace...</span>
      </div>
    </div>
  );
}

export function lazyLoad<T extends ComponentType<unknown>>(
  importFn: () => Promise<{ default: T }>
): LazyExoticComponent<T> {
  return lazy(importFn);
}

export function withSuspense(element: React.ReactNode) {
  return <Suspense fallback={<RouteLoadingFallback />}>{element}</Suspense>;
}