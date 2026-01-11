import { defineConfig, loadEnv, type ConfigEnv } from 'vite'
import react from '@vitejs/plugin-react'

import path from "path"

// https://vite.dev/config/
export default defineConfig(({ mode }: ConfigEnv) => {
  // Načtení env proměnných (process.cwd() je root projektu)
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      proxy: {
        '/api': {
          // Použije VITE_API_BASE_URL, pokud existuje, jinak localhost
          target: env.VITE_API_BASE_URL || 'http://localhost:3000',
          changeOrigin: true,
        },
      },
    },
  }
})
