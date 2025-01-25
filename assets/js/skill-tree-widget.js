document.addEventListener('alpine:init', () => {
    Alpine.data('skillSelector', () => ({
        viewMode: 'search', // 'search' or 'tree'
        searchQuery: '',
        categories: [],
        selectedSkills: [],
        allSkills: [],

        init() {
            // Initialize from Alpine store
            const skillStore = Alpine.store('skills');
            
            // Convert skills data to hierarchical structure
            this.loadSkillsData(skillStore.tagulousSettings || {});
            
            // Load initial selected skills
            if (skillStore.initialTags?.length) {
                this.loadInitialSkills(skillStore.initialTags);
            }
        },

        loadSkillsData(settings) {
            // Convert skills data to hierarchical structure
            const skillsData = settings.autocomplete_choices || [];
            const store = Alpine.store('skills');
            
            // Create flat list of all skills
            this.allSkills = skillsData.map(skill => ({
                id: skill[0],
                label: skill[1],
                icon: store.iconMapping[skill[1]] || 'heroicons:academic-cap',
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

        loadInitialSkills(initialTags) {
            initialTags.forEach(tag => {
                const skill = this.allSkills.find(s => s.id === tag[0]);
                if (skill) {
                    this.selectedSkills.push({
                        ...skill,
                        proficiency: 'required'
                    });
                }
            });
        },

        get filteredSkills() {
            if (!this.searchQuery) return this.allSkills;
            const query = this.searchQuery.toLowerCase();
            return this.allSkills.filter(skill => 
                skill.label.toLowerCase().includes(query)
            );
        },

        get skillsJson() {
            return JSON.stringify(
                this.selectedSkills.map(skill => ({
                    skill: skill.id,
                    proficiency: skill.proficiency,
                    name: skill.label
                }))
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

            // Update hidden input if it exists
            const input = document.querySelector('input[name="skills"]');
            if (input) {
                input.value = this.skillsJson;
                input.dispatchEvent(new Event('change', { bubbles: true }));
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
        }
    }));
});
