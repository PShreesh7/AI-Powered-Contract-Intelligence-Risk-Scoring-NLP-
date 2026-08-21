import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      // Forward API calls to the FastAPI/Flask backend during development.
      // Adjust target to match wherever text_utils.py's server is running.
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
