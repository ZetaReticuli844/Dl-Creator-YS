// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    allowedHosts: [
      'a23dd22fd52f.ngrok-free.app' // add your ngrok domain here
    ]
  }
})
