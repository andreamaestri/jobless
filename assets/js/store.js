// Alpine.js Store
document.addEventListener('alpine:init', () => {
    Alpine.store('modals', {
        skills: {
            open: false,
            show() {
                this.open = true;
                document.body.style.overflow = 'hidden';
            },
            close() {
                this.open = false;
                document.body.style.overflow = '';
            }
        }
    });

    Alpine.store('skills', {
        selected: [],
        updateSelected(skills) {
            this.selected = skills;
            this.updateFormDisplay();
        },
        updateFormDisplay() {
            const container = document.querySelector('.selected-skills');
            if (!container) return;

            if (this.selected.length === 0) {
                container.innerHTML = `
                    <div class="text-base-content/60 text-sm">
                        Click 'Manage Skills' to add required skills
                    </div>
                `;
                return;
            }

            container.innerHTML = this.selected.map(skill => `
                <div class="badge badge-lg gap-2 p-3 skill-badge ${this.getProficiencyClass(skill.proficiency)}">
                    <iconify-icon icon="${skill.icon}" class="text-lg"></iconify-icon>
                    <span>${skill.label}</span>
                    <span class="opacity-60">(${this.formatProficiency(skill.proficiency)})</span>
                </div>
            `).join('');
        },
        getProficiencyClass(proficiency) {
            const classes = {
                'required': 'badge-primary',
                'preferred': 'badge-secondary',
                'bonus': 'badge-accent'
            };
            return classes[proficiency] || 'badge-neutral';
        },
        formatProficiency(proficiency) {
            const labels = {
                'required': 'Required',
                'preferred': 'Preferred',
                'bonus': 'Nice to Have'
            };
            return labels[proficiency] || proficiency;
        }
    });
});

// Skill Selector Component
Alpine.data('skillSelector', () => ({
    viewMode: 'search',
    searchQuery: '',
    categories: [],
    selectedSkills: [],
    allSkills: [],

    init() {
        // Load skills data from window.TAGULOUS_SETTINGS
        const settings = window.TAGULOUS_SETTINGS || {};
        this.loadSkillsData(settings);
        
        // Load initial selected skills from store
        this.selectedSkills = Alpine.store('skills').selected;
    },

    loadSkillsData(settings) {
        // Convert skills data to hierarchical structure
        const skillsData = settings.autocomplete_choices || [];
        
        // Create flat list of all skills
        this.allSkills = skillsData.map(skill => ({
            id: skill[0],
            label: skill[1],
            icon: window.SKILL_MAPPINGS.icons[skill[1]] || 'heroicons:academic-cap',
            path: skill[2] || ''
        }));

        // Build categories
        const categoryMap = new Map();
        this.allSkills.forEach(skill => {
            const pathParts = skill.path.split(':');
            if (pathParts.length > 1) {
                const categoryPath = pathParts.slice(0, -1).join(':');
                const categoryName = pathParts[pathParts.length - 2] || 'Uncategorized';
                
                if (!categoryMap.has(categoryPath)) {
                    categoryMap.set(categoryPath, {
                        path: categoryPath,
                        label: categoryName,
                        skills: [],
                        expanded: false
                    });
                }
                categoryMap.get(categoryPath).skills.push(skill);
            }
        });

        this.categories = Array.from(categoryMap.values());
    },

    get filteredSkills() {
        if (!this.searchQuery) return this.allSkills;
        const query = this.searchQuery.toLowerCase();
        return this.allSkills.filter(skill => 
            skill.label.toLowerCase().includes(query)
        );
    },

    toggleCategory(category) {
        category.expanded = !category.expanded;
    },

    isSelected(skillId) {
        return this.selectedSkills.some(s => s.id === skillId);
    },

    toggleSkill(skill) {
        if (this.isSelected(skill.id)) {
            this.removeSkill(skill);
        } else {
            this.addSkill(skill);
        }
    },

    addSkill(skill) {
        if (!this.isSelected(skill.id)) {
            this.selectedSkills.push({
                ...skill,
                proficiency: 'required'
            });
        }
    },

    removeSkill(skill) {
        this.selectedSkills = this.selectedSkills.filter(s => s.id !== skill.id);
    },

    updateSkill(skill) {
        const index = this.selectedSkills.findIndex(s => s.id === skill.id);
        if (index !== -1) {
            this.selectedSkills[index] = { ...skill };
        }
    },

    saveSkills() {
        // Update hidden input
        const input = document.querySelector('#id_skills');
        if (input) {
            input.value = JSON.stringify(
                this.selectedSkills.map(skill => ({
                    skill: skill.id,
                    proficiency: skill.proficiency,
                    name: skill.label
                }))
            );
        }

        // Update store and UI
        Alpine.store('skills').updateSelected(this.selectedSkills);
        
        // Close modal
        Alpine.store('modals').skills.close();
    }
}));
