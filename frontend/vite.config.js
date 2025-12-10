import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/', // Use root base for local dev to support both /films and /books
  build: {
    // Force fresh build by modifying output config
    rollupOptions: {
      output: {
        manualChunks: undefined,
      }
    }
  }
})
