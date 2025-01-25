import 'vite/modulepreload-polyfill'
import Alpine from 'alpinejs'

// Initialize Alpine data stores and components
function initializeComponents() {
    // Modal component
    Alpine.data('skillsModal', () => ({
        isMobile: window.innerWidth < 640,

        init() {
            this.setupEventListeners();
        },

        setupEventListeners() {
            window.addEventListener('resize', () => {
                this.isMobile = window.innerWidth < 640;
            });
        },

        get store() {
            return Alpine.store('app').skills;
        },

        get modal() {
            return this.store.modal;
        },

        handleSearch(query) {
            this.store.filterSkills(query);
        },

        save() {
            if (this.modal.ready) {
                window.dispatchEvent(new CustomEvent('skills-updated', { detail: this.store.selected }));
                this.store.closeModal();
            }
        },
    }));
}

// Export initialization function
export function init() {
    initializeComponents();
}

// Initialize when Alpine loads
document.addEventListener('alpine:init', init);
