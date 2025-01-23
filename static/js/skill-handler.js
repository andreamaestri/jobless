document.addEventListener('alpine:init', () => {
    Alpine.data('skillSelector', () => ({
        open: false,
        selectedSkills: [],
        searchQuery: '',
        showSuggestions: false,
        filteredSkills: [],
        
        init() {
            // Initialize with closed modal
            this.open = false;
            
            // Get initial skills if any
            const skillsInput = document.getElementById('id_skills');
            if (skillsInput && skillsInput.value) {
                const skillNames = skillsInput.value.split(',')
                    .map(s => s.trim())
                    .filter(Boolean);

                this.selectedSkills = skillNames.map(name => ({
                    name: name,
                    icon: window.MODAL_ICON_MAPPING[name.toLowerCase()] || 'heroicons:academic-cap',
                    icon_dark: window.MODAL_DARK_VARIANTS[window.MODAL_ICON_MAPPING[name.toLowerCase()] || 'heroicons:academic-cap'] || window.MODAL_ICON_MAPPING[name.toLowerCase()] || 'heroicons:academic-cap'
                }));
            }

            // Listen for skills-updated events
            window.addEventListener('skills-updated', event => {
                this.updateSkills(event.detail);
            });

            // Listen for toggle-skill events
            window.addEventListener('toggle-skill', event => {
                const skillToRemove = event.detail;
                this.selectedSkills = this.selectedSkills.filter(s => s.name !== skillToRemove.name);
                this.updateSkills(this.selectedSkills);
            });
        },

        toggleModal() {
            this.open = !this.open;
            if (!this.open) {
                this.searchQuery = '';
                this.showSuggestions = false;
            }
        },

        updateSkills(skills) {
            this.selectedSkills = skills;
            const skillsInput = document.getElementById('id_skills');
            if (skillsInput) {
                skillsInput.value = skills.map(s => s.name).join(',');
                skillsInput.dispatchEvent(new Event('change', { bubbles: true }));
            }
        },

        addSkill(skill) {
            if (!this.selectedSkills.find(s => s.name === skill.name)) {
                this.selectedSkills.push({
                    name: skill.name,
                    icon: window.MODAL_ICON_MAPPING[skill.name.toLowerCase()] || 'heroicons:academic-cap',
                    icon_dark: window.MODAL_DARK_VARIANTS[window.MODAL_ICON_MAPPING[skill.name.toLowerCase()] || 'heroicons:academic-cap'] || window.MODAL_ICON_MAPPING[skill.name.toLowerCase()] || 'heroicons:academic-cap'
                });
                this.updateSkills(this.selectedSkills);
            }
            this.searchQuery = '';
            this.showSuggestions = false;
        },

        removeSkill(skill) {
            this.selectedSkills = this.selectedSkills.filter(s => s.name !== skill.name);
            this.updateSkills(this.selectedSkills);
        },

        handleKeydown(event) {
            if (event.key === 'Escape') {
                this.searchQuery = '';
                this.showSuggestions = false;
            }
        }
    }));
});