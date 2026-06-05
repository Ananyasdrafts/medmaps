import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base is "/medmaps/" for the GitHub Pages build, "/" for local dev
export default defineConfig(({ command }) => ({
  base: command === "build" ? "/medmaps/" : "/",
  plugins: [react()],
  server: { port: 5173 },
}));
