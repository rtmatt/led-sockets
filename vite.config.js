import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import path from 'node:path';
import process from 'node:process';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools()
  ],
  build: {
    outDir: '../dist'
  },
  root: 'src',
  envDir: '../',
  publicDir: '../public',
  resolve: {
    alias: {
      '/src': path.resolve(process.cwd(), 'src'),
      '@': fileURLToPath(new URL('./src/ts', import.meta.url))
    }
  }
});
