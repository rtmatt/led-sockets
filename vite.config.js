import { defineConfig } from 'vite';
import path from 'node:path';
import process from 'node:process';

export default defineConfig({
  build: {
    outDir: '../dist'
  },
  root: 'src',
  publicDir: '../public',
  resolve: {
    alias: { '/src': path.resolve(process.cwd(), 'src') }
  }
})
