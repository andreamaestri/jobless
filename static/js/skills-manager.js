import 'vite/modulepreload-polyfill'
import Alpine from 'alpinejs'

document.addEventListener('alpine:init', () => {
    Alpine.data('skillSelector', () => ({
        searchQuery: '',
        showSuggestions: false,
        selectedCategory: '',
        selectedIndex: -1,

        init() {
            // Watch for search input changes
            this.$watch('searchQuery', (value) => {
                this.store.filterSkills(value);
            });
        },

        get store() {
            return Alpine.store('app').skills;
        },

        handleEnter() {
            if (this.selectedIndex >= 0 && this.store.filteredSkills[this.selectedIndex]) {
                const skill = this.store.filteredSkills[this.selectedIndex];
                this.addSkill({ name, icon });
            }
        },

        addSkill(skill) {
            if (this.store.add(skill)) {
                this.searchQuery = '';
                this.closeSuggestions();
            }
        },

        removeSkill(skillName) {
            this.store.remove(skillName);
        }
    }));
});

// Export initialization function
export function init() {
    // Any additional initialization if needed
}
