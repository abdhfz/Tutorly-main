import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  base: './',
  plugins: [react()],
  publicDir: false,
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5000',
      '/static/logo.png': 'http://localhost:5000',
      '/static/favicon.ico': 'http://localhost:5000',
    },
  },
  build: {
    outDir: 'static',
    emptyOutDir: false,
  },
});
