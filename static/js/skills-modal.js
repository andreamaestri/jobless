import Alpine from 'alpinejs'

// Initialize Alpine data stores and components
document.addEventListener('alpine:init', () => {
    // Skills Modal Component
    Alpine.data('skillsModal', () => ({
        isMobile: window.innerWidth < 640,
        isSearchFocused: false,

        init() {
            this.setupEventListeners();
        },

        setupEventListeners() {
            // Handle window resize
            window.addEventListener('resize', () => {
                this.isMobile = window.innerWidth < 640;
            });

            // Initialize icons after skills update
            window.addEventListener('skills-updated', () => {
                if (window.skillIconsHelper) {
                    window.skillIconsHelper.updateIcons();
                }
            });
        },

        // Access to global store
        get store() {
            return Alpine.store('app').skills;
        },

        get modal() {
            return this.store.modal;
        },

        // Handle skill search
        handleSearch(query) {
            this.store.filterSkills(query);
        },

        // Save selected skills
        save() {
            if (this.modal.ready) {
                // Update Tagulous hidden input value and trigger change event
                const input = document.getElementById('id_skills');
                if (input) {
                    const selectedSkills = this.store.selected.map(s => s.name).join(',');
                    input.value = selectedSkills;
                    input.dispatchEvent(new Event('change', { bubbles: true }));
                }

                // Notify components of update
                window.dispatchEvent(new CustomEvent('skills-updated', { 
                    detail: this.store.selected 
                }));

                // Close modal
                this.store.closeModal();
            }
        }
    }));
});

// Initialize when module is imported
export function init() {
    // Any additional initialization if needed
}

// Auto-initialize
init();
