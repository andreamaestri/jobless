import Alpine from 'alpinejs'
import { persist } from '@alpinejs/persist'

// Tag input component
Alpine.data('tagInput', () => ({
    tags: [],
    input: '',
    suggestions: [],
    loading: false,
    persist: true,

    init() {
        this.tags = Alpine.$persist(this.tags).as('tags');
        const existingTags = this.$refs.hiddenInput?.value;
        if (existingTags) {
            this.tags = existingTags.split(',').map(t => t.trim());
        }
    },

    async fetchSuggestions() {
        if (this.input.length < 2) {
            this.suggestions = [];
            return;
        }

        this.loading = true;
        try {
            const response = await fetch(`/jobs/skills-autocomplete/?q=${encodeURIComponent(this.input)}`);
            const data = await response.json();
            this.suggestions = data.results || [];
        } catch (error) {
            console.error('Error fetching suggestions:', error);
            this.suggestions = [];
        } finally {
            this.loading = false;
        }
    },

    addTag(tag) {
        if (!this.tags.includes(tag)) {
            this.tags.push(tag);
            this.updateHiddenInput();
        }
        this.input = '';
        this.suggestions = [];
    },

    removeTag(index) {
        this.tags.splice(index, 1);
        this.updateHiddenInput();
    },

    updateHiddenInput() {
        if (this.$refs.hiddenInput) {
            this.$refs.hiddenInput.value = this.tags.join(',');
            // Dispatch change event to trigger form validation
            this.$refs.hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    },

    handleKeydown(e) {
        if (e.key === 'Enter' && this.input) {
            e.preventDefault();
            this.addTag(this.input);
        } else if (e.key === 'Backspace' && !this.input && this.tags.length > 0) {
            this.removeTag(this.tags.length - 1);
        }
    }
}));

// Initialize when Alpine loads
document.addEventListener('alpine:init', () => {
    Alpine.plugin(persist);
});

export default {};