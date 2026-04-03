export default {
  budgets: [
    {
      type: 'chunk',
      name: 'index',
      maxSizeKb: 8,
    },
    {
      type: 'chunk',
      name: 'react-vendor',
      maxSizeKb: 70,
    },
    {
      type: 'chunk',
      name: 'forms',
      maxSizeKb: 25,
    },
    {
      type: 'chunk',
      name: 'network',
      maxSizeKb: 20,
    },
  ],
  totalBudgetSizeKb: 160,
  onBudgetExceeded: 'error',
  baseline: {
    date: '2026-04-03',
    totalGzipSizeKb: 140.85,
    chunks: {
      'react-vendor': 63.34,
      forms: 21.83,
      network: 14.86,
      index: 4.0,
    },
  },
};
