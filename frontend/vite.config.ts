import { readFileSync } from 'fs'
import { dirname, resolve } from 'path'
import { fileURLToPath } from 'url'
import react from '@vitejs/plugin-react'
import yaml from 'js-yaml'
import { defineConfig } from 'vite'

const __dirname = dirname(fileURLToPath(import.meta.url))

// config.yml lives one level above the frontend directory (project root)
function loadConfig(): Record<string, unknown> {
  try {
    const raw = readFileSync(resolve(__dirname, '../config.yml'), 'utf-8')
    return (yaml.load(raw) as Record<string, unknown>) ?? {}
  } catch {
    return {}
  }
}

const cfg        = loadConfig()
const srv        = (cfg.server ?? {}) as Record<string, unknown>
const appCfg     = (cfg.app    ?? {}) as Record<string, unknown>

const frontendPort = Number(srv.frontend_port ?? 3000)
const backendPort  = Number(srv.backend_port  ?? 8000)
const appName      = String(appCfg.name    ?? 'CriteriaMeter')
const appVersion   = String(appCfg.version ?? '0.1.0')

export default defineConfig({
  plugins: [react()],

  // Injected as compile-time constants; accessed via src/config.ts
  define: {
    __APP_NAME__:    JSON.stringify(appName),
    __APP_VERSION__: JSON.stringify(appVersion),
  },

  server: {
    host: '0.0.0.0',
    port: frontendPort,
    proxy: {
      '/api': `http://localhost:${backendPort}`,
    },
  },

  preview: {
    host: '0.0.0.0',
    port: frontendPort,
  },
})
