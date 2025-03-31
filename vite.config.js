import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    }
  },
  server: {
    fs: {
      // Allow serving files from one level up to the project root
      allow: ['..']
    }
  },
  optimizeDeps: {
    include: ['@fortawesome/fontawesome-free']
  }
}) 