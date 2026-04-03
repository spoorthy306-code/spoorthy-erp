# Deprecated and Removed Code

## Removed on 2026-04-03

### Legacy chart components
- `src/components/charts/BarChart.tsx`
- `src/components/charts/DonutChart.tsx`
- `src/components/charts/GaugeChart.tsx`
- `src/components/charts/LineChart.tsx`
- `src/components/charts/WaterfallChart.tsx`
- `src/components/charts/index.ts`

Reason:
- These files depended on `recharts` and were not part of the active routed frontend.
- The active dashboard now uses lightweight inline SVG charts in `src/components/dashboard/Charts.tsx`.
- This cleanup removed dead code and allowed the `recharts` dependency to be dropped.

### Legacy dashboard pages
- `src/pages/Dashboard.jsx`
- `src/pages/Reports/Dashboard.jsx`

Reason:
- These pages were not part of the active TypeScript route tree.
- They risked ambiguous import resolution with the new routed pages.

## Dependency removed
- `recharts`

Reason:
- No active route now requires it.
- Bundle size protection is enforced through CI and a local bundle budget script.

## Recovery
- Restore from git history if any archived implementation is needed again.
