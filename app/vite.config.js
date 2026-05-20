import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/** Serve public/manual/ before the SPA index.html fallback on /manual and /manual/. */
function manualStaticPlugin() {
  return {
    name: 'manual-static',
    configureServer(server) {
      server.middlewares.use((req, _res, next) => {
        const path = req.url?.split('?')[0] ?? ''
        if (path === '/manual' || path === '/manual/') {
          req.url = '/manual/index.html' + (req.url?.includes('?') ? '?' + req.url.split('?')[1] : '')
        }
        next()
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), manualStaticPlugin()],
  server: {
    fs: {
      allow: [".."],
    },
  },
})
