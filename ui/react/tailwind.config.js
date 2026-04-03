/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: '#2563EB',
        growth: '#059669',
        danger: '#DC2626',
        warning: '#F59E0B',
        success: '#10B981',
        surface: '#F9FAFB',
        ink: '#111827',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
      },
      boxShadow: {
        panel: '0 10px 40px -16px rgba(17, 24, 39, 0.25)',
      },
    },
  },
  plugins: [],
};
