import Alpine from 'alpinejs'

// Initialize Alpine data stores and components
document.addEventListener('alpine:init', () => {
    // Skills Modal Component
    Alpine.data('skillsModal', () => ({
        isMobile: window.innerWidth < 640,
        isSearchFocused: false,
        searchQuery: '',
        suggestions: [],
        showSuggestions: false,
        selectedIndex: -1,

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

        // Tagulous autocomplete integration
        async handleTagSearch(query) {
            if (!query || query.length < 2) {
                this.suggestions = [];
                return;
            }

            try {
                const response = await fetch(`/jobs/skills/autocomplete/?q=${encodeURIComponent(query)}`);
                if (!response.ok) throw new Error('Failed to fetch suggestions');
                
                const data = await response.json();
                this.suggestions = data.results;
                this.showSuggestions = true;
                this.selectedIndex = -1;
            } catch (error) {
                console.error('Error fetching suggestions:', error);
                this.suggestions = [];
            }
        },

        navigateSuggestion(direction) {
            const newIndex = this.selectedIndex + direction;
            if (newIndex >= -1 && newIndex < this.suggestions.length) {
                this.selectedIndex = newIndex;
            }
        },

        handleEnter() {
            const suggestion = this.suggestions[this.selectedIndex];
            if (suggestion) {
                this.addSkill(suggestion);
            } else if (this.searchQuery.trim()) {
                // Allow custom skills if no suggestion selected
                this.addSkill({ name: this.searchQuery.trim() });
            }
        },

        addSkill(skill) {
            if (this.store.add(skill)) {
                this.searchQuery = '';
                this.suggestions = [];
                this.showSuggestions = false;
            }
        },

        closeSuggestions() {
            setTimeout(() => {
                this.showSuggestions = false;
                this.selectedIndex = -1;
            }, 200);
        },

        // Handle skill search (for filtering existing skills)
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
