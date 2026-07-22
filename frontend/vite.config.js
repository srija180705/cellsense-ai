import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev server proxies /api -> FastAPI backend on :8000 (no CORS hassle).
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
});
