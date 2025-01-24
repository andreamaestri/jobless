import 'vite/modulepreload-polyfill'

// Import Alpine.js and plugins
import Alpine from 'alpinejs'
import persist from '@alpinejs/persist'
import focus from '@alpinejs/focus'

// Import your other JS modules
import './store'
import './skills-modal'
import './skill-icons'
import './skills-select'
import './skills-manager'
import './form-handler'
import './script'
import './toast'

// Import external libraries
import 'iconify-icon'

// Initialize Alpine
window.Alpine = Alpine
Alpine.plugin(persist)
Alpine.plugin(focus)
Alpine.start()