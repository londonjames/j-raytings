import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/', // Use root base for local dev to support both /films and /books
  server: {
    host: '0.0.0.0', // Allow connections from network
    port: 5174,
  },
  build: {
    // Force fresh build by modifying output config
    rollupOptions: {
      output: {
        manualChunks: undefined,
      }
    }
  }
})
