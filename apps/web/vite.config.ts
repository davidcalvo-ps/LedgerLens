import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// The browser only talks to the Django core API. The AI service is never
// reachable from the web app, so there is deliberately no proxy for it.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
    },
  },
});
