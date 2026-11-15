import react from '@vitejs/plugin-react'
import { defineConfig } from 'vitest/config'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      '/api': process.env.API_PROXY_TARGET ?? "http://localhost:8000"
    }
  },
  test: {
    environment: "jsdom"
  }
})
