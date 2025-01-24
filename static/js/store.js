import Alpine from 'alpinejs'
import { persist } from '@alpinejs/persist'

// Page state methods (stored separately to avoid persistence issues)
const pageStateMethods = {
    init() {
        // Remove the hasOwnProperty check as it's causing issues
        // Initial loading state
        setTimeout(() => {
            this.isLoading = false;
        }, 100);

        // Initialize after Alpine is ready
        document.addEventListener("alpine:initialized", () => {
            this.setupEventListeners();
        });
    },
    setupEventListeners() {
        // Handle page visibility changes
        document.addEventListener("visibilitychange", () => {
            if (document.visibilityState === "visible") {
                this.isLoading = false;
            }
        });
        
        // Handle page transitions
        window.addEventListener("beforeunload", () => {
            this.isLoading = true;
        });
    }
};

// Global Store initialization
export function initializeStore() {
    // Global Store
    Alpine.store('app', {
        theme: {
            current: 'Jobless',
            themes: ['Jobless', 'Dark', 'lofi', 'pastel'],
            set(theme) {
                this.current = theme;
                document.documentElement.setAttribute('data-theme', theme);
            }
        },
        sidebar: {
            open: false,
            collapsed: false,
            toggle() {
                this.open = !this.open;
            },
            collapse() {
                this.collapsed = !this.collapsed;
            }
        },
        pageState: {
            isLoading: false,
            init() {
                pageStateMethods.init.call(this);
            },
            setupEventListeners() {
                pageStateMethods.setupEventListeners.call(this);
            }
        }
    });

    // Initialize persisted values
    Alpine.effect(() => {
        // Access and persist theme
        const persistedTheme = Alpine.$persist(Alpine.store('app').theme).as('app_theme');
        Alpine.store('app').theme.current = persistedTheme.current;

        // Access and persist sidebar state
        const persistedSidebar = Alpine.$persist(Alpine.store('app').sidebar).as('app_sidebar');
        Alpine.store('app').sidebar.open = persistedSidebar.open;
        Alpine.store('app').sidebar.collapsed = persistedSidebar.collapsed;
    });

    // Initialize page state
    Alpine.store('app').pageState.init();
}

// Initialize when Alpine loads
document.addEventListener('alpine:init', initializeStore);

export default {
    initializeStore
};
