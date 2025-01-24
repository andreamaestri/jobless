import { defineConfig } from 'vite'
import { resolve } from 'path'

export default defineConfig({
    base: '/static/',
    build: {
        manifest: true,
        outDir: resolve('./static'),
        rollupOptions: {
            input: {
                // Main application bundle
                main: resolve('./static/js/main.js'),
                
                // Skills management
                skills: resolve('./static/js/skills-modal.js'),
                skillIcons: resolve('./static/js/skill-icons.js'),
                skillsSelect: resolve('./static/js/skills-select.js'),
                skillsManager: resolve('./static/js/skills-manager.js'),
                
                // Form handling
                formHandler: resolve('./static/js/form-handler.js'),
                
                // Core functionality
                store: resolve('./static/js/store.js'),
                script: resolve('./static/js/script.js'),
                
                // Utilities
                toast: resolve('./static/js/toast.js'),
            },
            output: {
                chunkFileNames: 'js/[name]-[hash].js',
                entryFileNames: 'js/[name]-[hash].js',
                assetFileNames: 'assets/[name]-[hash][extname]'
            }
        }
    },
    server: {
        origin: 'http://localhost:5173',
        cors: true,
        port: 5173,
        strictPort: true,
        hmr: {
            protocol: 'ws',
            host: 'localhost',
        }
    },
    resolve: {
        alias: {
            '@': resolve('./static')
        }
    }
})
