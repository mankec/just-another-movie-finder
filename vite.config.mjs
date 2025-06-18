import { resolve } from 'path'
import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  root: '.',
  build: {
    outDir: "./static/build",
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, './src/js/main.js'),
      }
    }
  },
  server: {
    hmr: false
  },
  plugins: [
    tailwindcss(),
  ],
})
