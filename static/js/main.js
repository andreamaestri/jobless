import 'vite/modulepreload-polyfill'

// Import Alpine.js and plugins
import Alpine from 'alpinejs'
import persist from '@alpinejs/persist'
import focus from '@alpinejs/focus'
import 'iconify-icon' 
import { animations } from './script'
import { registerMotion } from './motion'

// Keep the production entrypoint fingerprinted when frontend fixes are deployed.

// Initialize Alpine
window.Alpine = Alpine
Alpine.plugin(persist)
Alpine.plugin(focus)
registerMotion(Alpine, animations)
Alpine.start()
window.__JOBLESS_BUILD__ = 'jobs-add-fix'

// Core initialization - base store and features
import './store'

// Register skill tree component
import './skill-tree-widget'

// On-demand imports for specific features
const featureModules = {
    'script': () => import('./script'),
    'toast': () => import('./toast'),
    'tag-input': () => import('./tag-input'),
    'skills-modal': () => import('./skills-modal'),
    'skill-icons': () => import('./skill-icons'),
    'skills-select': () => import('./skills-select'),
    'skills-manager': () => import('./skills-manager'),
    'skill-tree-widget': () => import('./skill-tree-widget'),
    'events': () => import('./events')
}

// Initialize feature modules based on data attributes
document.addEventListener('DOMContentLoaded', () => {
    // Get required features from data attribute
    const features = document.documentElement.dataset.features?.split(' ') || []
    
    // Load required feature modules
    features.forEach(feature => {
        if (featureModules[feature]) {
            featureModules[feature]()
                .then(() => console.log(`Loaded ${feature} module`))
                .catch(err => console.warn(`Failed to load ${feature} module:`, err))
        }
    })
})
