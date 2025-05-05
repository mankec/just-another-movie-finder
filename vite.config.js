import { resolve } from 'path'

export default {
  root: 'static',
  build: {
    outDir: "./build",
    emptyOutDir: true,
    manifest: true,
    rollupOptions: {
      input: {
        main: resolve(__dirname, './static/js/main.js'),
      }
    }
  }
}
