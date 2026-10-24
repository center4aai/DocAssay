import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // changeOrigin: the backend answers only its own Host header values.
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
});