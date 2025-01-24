import Alpine from 'alpinejs'
import { persist } from '@alpinejs/persist'

// Initialize Alpine stores
function initializeStores() {
    Alpine.store('theme', {
        themes: ["Jobless", "Dark", "lofi", "pastel"],
        current: localStorage.getItem("theme") || "Jobless",
        toggle() {
            this.current = this.current === "Jobless" ? "Dark" : "Jobless";
            localStorage.setItem("theme", this.current);
            document.documentElement.setAttribute("data-theme", this.current);
        }
    });

    Alpine.store('sidebar', {
        open: window.innerWidth >= 1024,
        collapsed: JSON.parse(localStorage.getItem("sidebarCollapsed") || "false"),
        toggle() {
            this.open = !this.open;
        },
        collapse() {
            this.collapsed = !this.collapsed;
            localStorage.setItem("sidebarCollapsed", this.collapsed);
        }
    });

    Alpine.store('pageState', {
        isLoading: false,
        setLoading(state) {
            this.isLoading = state;
        }
    });

    // Skills store with persistence
    Alpine.store('skills', {
        selected: Alpine.$persist([]).as('selected_skills'),
        
        init() {
            const skillsInput = document.getElementById('id_skills');
            if (skillsInput?.value) {
                this.selected = skillsInput.value.split(',').map(s => s.trim());
            }
        },
        
        isSelected(skillName) {
            return this.selected.includes(skillName);
        },
        
        toggle(skillName) {
            if (this.isSelected(skillName)) {
                this.selected = this.selected.filter(s => s !== skillName);
            } else {
                this.selected.push(skillName);
            }
            this.updateHiddenInput();
        },
        
        setSelected(skills) {
            this.selected = Array.isArray(skills) ? skills : [];
            this.updateHiddenInput();
        },

        updateHiddenInput() {
            const hiddenInput = document.getElementById('id_skills');
            if (hiddenInput) {
                hiddenInput.value = this.selected.join(',');
                hiddenInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }
    });
}

// Initialize Alpine data stores and components
function initializeComponents() {
    // Skill selector component
    Alpine.data('skillSelector', () => ({
        searchQuery: '',
        showSuggestions: false,
        selectedIndex: -1,
        browserSearch: '',
        selectedCategory: '',
        categories: [],
        skillsList: [],

        init() {
            if (window.SKILL_ICONS) {
                this.skillsList = window.SKILL_ICONS.map(([icon, name]) => ({ icon, name }));
                this.categories = [...new Set(this.skillsList.map(skill => skill.icon.split(':')[0]))];
            }
        },

        get selectedSkills() {
            return Alpine.store('skills').selected;
        },

        isSelected(skillName) {
            return Alpine.store('skills').isSelected(skillName);
        },

        addSkill(skillName) {
            if (!this.isSelected(skillName)) {
                Alpine.store('skills').toggle(skillName);
            }
            this.searchQuery = '';
            this.showSuggestions = false;
        },

        removeSkill(skillName) {
            Alpine.store('skills').toggle(skillName);
        },

        get computedFilteredSkills() {
            if (!this.searchQuery) return [];
            return this.skillsList
                .filter(skill => !this.selectedSkills.includes(skill.name))
                .filter(skill => skill.name.toLowerCase().includes(this.searchQuery.toLowerCase()))
                .slice(0, 10);
        },

        get filteredBrowserSkills() {
            return this.skillsList.filter(skill => {
                const matchesSearch = !this.browserSearch || 
                    skill.name.toLowerCase().includes(this.browserSearch.toLowerCase());
                const matchesCategory = !this.selectedCategory || 
                    skill.icon.startsWith(this.selectedCategory + ':');
                return matchesSearch && matchesCategory;
            });
        },

        handleQuickSelect(event, skill) {
            if (!skill?.name) return;
            if (this.isSelected(skill.name)) {
                this.removeSkill(skill.name);
            } else {
                this.addSkill(skill.name);
            }
        },

        handleKeyboardNavigation(direction) {
            const max = this.computedFilteredSkills.length - 1;
            this.selectedIndex = Math.max(-1, Math.min(max, this.selectedIndex + direction));
        }
    }));

    // Modal component
    Alpine.data('skillsModal', () => ({
        open: false,
        ready: false,
        isMobile: window.innerWidth < 640,
        isSearchFocused: false,
        search: '',

        init() {
            this.setupEventListeners();
            this.ready = true;
            this.open = false;
        },

        setupEventListeners() {
            window.addEventListener('resize', () => {
                this.isMobile = window.innerWidth < 640;
            });
        },

        handleSkillsUpdate(event) {
            if (!this.ready) return;
            if (event?.detail?.selectedSkills) {
                Alpine.store('skills').setSelected(event.detail.selectedSkills);
            }
        },

        filterSkills() {
            if (!window.SKILL_ICONS) return;
            const searchTerm = this.search.toLowerCase();
            this.filteredSkills = window.SKILL_ICONS
                .filter(([_, name]) => !searchTerm || name.toLowerCase().includes(searchTerm));
        },

        save() {
            if (this.ready) {
                this.$dispatch('skills-updated', Alpine.store('skills').selected);
                this.close();
            }
        },

        cancel() {
            window.dispatchEvent(new CustomEvent('skills-restored'));
            this.close();
        },

        close() {
            this.open = false;
            this.search = '';
            this.filteredSkills = [];
        }
    }));
}

// Initialize everything when Alpine loads
document.addEventListener('alpine:init', () => {
    Alpine.plugin(persist);
    initializeStores();
    initializeComponents();
});

export default {
    initializeStores,
    initializeComponents
};
