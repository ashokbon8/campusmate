import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// The dev server proxies `/api/*` to the FastAPI backend so the browser can use
// same-origin requests in development. In production the same `/api` prefix is
// served by the reverse proxy defined in docker-compose (see nginx.conf).
const apiTarget = process.env.VITE_API_TARGET || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    // Allows the dev server to be reached through the sandbox/proxy hostnames.
    allowedHosts: true,
    proxy: {
      "/api": {
        target: apiTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
  preview: {
    port: 4173,
    host: true,
  },
});
