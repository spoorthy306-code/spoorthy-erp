import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { fileURLToPath, URL } from 'node:url';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig(({ command }) => ({
  plugins: [
    react(),
    command === 'build'
      ? visualizer({
          open: false,
          gzipSize: true,
          brotliSize: true,
          template: 'treemap',
          filename: 'dist/stats.html',
          title: 'Spoorthy ERP Bundle Analysis',
        })
      : null,
  ].filter(Boolean),
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  build: {
    cssCodeSplit: true,
    chunkSizeWarningLimit: 450,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes('node_modules')) {
            return undefined;
          }

          if (id.includes('@tanstack/react-query')) {
            return 'react-query';
          }

          if (
            id.includes('react-hook-form') ||
            id.includes('@hookform/resolvers') ||
            id.includes('zod')
          ) {
            return 'forms';
          }

          if (id.includes('zustand')) {
            return 'state';
          }

          if (id.includes('axios')) {
            return 'network';
          }

          if (id.includes('react-router-dom')) {
            return 'router';
          }

          if (
            id.includes('/react/') ||
            id.includes('/react-dom/') ||
            id.includes('/scheduler/')
          ) {
            return 'react-vendor';
          }

          return 'vendor';
        },
      },
    },
  },
  server: { port: 5173 },
}));
