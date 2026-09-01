import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward all backend routes to FastAPI during development.
      // Note: using 127.0.0.1 instead of localhost to prevent IPv6 resolution issues on Node
      '/analyze': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/ask':     { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/health':  { target: 'http://127.0.0.1:8000', changeOrigin: true },
    }
  },
  build: {
    outDir: '../dist',   // build goes to legal-nlp-platform/dist
    emptyOutDir: true,
  }
})
