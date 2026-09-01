import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward all backend routes to FastAPI during development.
      '/analyze': { target: 'http://localhost:8000', changeOrigin: true },
      '/ask':     { target: 'http://localhost:8000', changeOrigin: true },
      '/health':  { target: 'http://localhost:8000', changeOrigin: true },
    }
  },
  build: {
    outDir: '../dist',   // build goes to legal-nlp-platform/dist
    emptyOutDir: true,
  }
})
