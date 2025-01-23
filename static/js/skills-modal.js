document.addEventListener('alpine:init', () => {
    Alpine.data('skillsModal', () => ({
        open: false,
        search: '',
        isSearchFocused: false,
        isMobile: window.innerWidth < 640,
        selectedSkills: [],
        lastSelected: null,
        currentLetter: null,
        iconMapping: {},
        darkVariants: {},
        defaultIcon: 'heroicons:academic-cap',

        init() {
            // Ensure modal starts closed
            this.open = false;
            
            // Initialize icon mappings after they're available
            this.iconMapping = window.MODAL_ICON_MAPPING || {};
            this.darkVariants = window.MODAL_DARK_VARIANTS || {};
            
            // Handle mobile detection
            this.isMobile = window.innerWidth < 640;
            window.addEventListener('resize', () => {
                this.isMobile = window.innerWidth < 640;
            });

            // Initialize selected skills from input if it exists
            const skillsInput = document.getElementById('id_skills');
            if (skillsInput && skillsInput.value) {
                const skillNames = skillsInput.value.split(',')
                    .map(s => s.trim())
                    .filter(Boolean);
                    
                this.selectedSkills = skillNames.map(name => ({
                    name: name,
                    icon: this.getIconForSkill(name),
                    icon_dark: this.getDarkIconForSkill(name)
                }));
            }
        },

        getIconForSkill(skillName) {
            return this.iconMapping[skillName.toLowerCase()] || this.defaultIcon;
        },

        getDarkIconForSkill(skillName) {
            const baseIcon = this.getIconForSkill(skillName);
            return this.darkVariants[baseIcon] || baseIcon;
        },

        handleSkillsUpdate(e) {
            if (!e?.detail?.selectedSkills) return;
            this.selectedSkills = e.detail.selectedSkills;
            // Only open modal if triggered by user action
            if (e.isTrusted) {
                this.open = true;
            }
        },

        isSelected(skillName) {
            return this.selectedSkills.some(s => s.name === skillName);
        },

        toggleSkill(skill) {
            const index = this.selectedSkills.findIndex(s => s.name === skill.name);
            if (index !== -1) {
                this.selectedSkills.splice(index, 1);
            } else {
                this.selectedSkills.push({
                    name: skill.name,
                    icon: this.getIconForSkill(skill.name),
                    icon_dark: this.getDarkIconForSkill(skill.name)
                });
            }
        },

        handleQuickSelect(event, skill) {
            if (event.shiftKey && this.lastSelected) {
                const skills = Array.from(this.$refs.skillsContainer.querySelectorAll('[data-skill]'));
                const start = skills.findIndex(s => s.dataset.skill && JSON.parse(s.dataset.skill).name === this.lastSelected.name);
                const end = skills.findIndex(s => s.dataset.skill && JSON.parse(s.dataset.skill).name === skill.name);
                const range = skills.slice(Math.min(start, end), Math.max(start, end) + 1);
                
                range.forEach(skillEl => {
                    if (skillEl.dataset.skill) {
                        const skillData = JSON.parse(skillEl.dataset.skill);
                        if (!this.isSelected(skillData.name)) {
                            this.toggleSkill(skillData);
                        }
                    }
                });
            } else {
                this.toggleSkill(skill);
                this.lastSelected = skill;
            }
        },

        handleSearch(e) {
            const query = e.target.value.toLowerCase();
            this.$refs.skillsContainer.querySelectorAll('.skill-group').forEach(group => {
                let hasVisible = false;
                group.querySelectorAll('.skill-card').forEach(card => {
                    const name = card.querySelector('.skill-name').textContent.toLowerCase();
                    const visible = !query || name.includes(query);
                    card.style.display = visible ? '' : 'none';
                    if (visible) hasVisible = true;
                });
                group.style.display = hasVisible ? '' : 'none';
            });
        },

        handleScroll(e) {
            if (!e.target) return;
            
            const container = e.target;
            const groups = container.querySelectorAll('.skill-group');
            let mostVisible = null;
            let maxVisibleHeight = 0;
            
            groups.forEach(group => {
                const rect = group.getBoundingClientRect();
                const visibleHeight = Math.min(rect.bottom, window.innerHeight) - 
                                    Math.max(rect.top, 0);
                
                if (visibleHeight > maxVisibleHeight) {
                    maxVisibleHeight = visibleHeight;
                    mostVisible = group;
                }
            });
            
            if (mostVisible) {
                const letter = mostVisible.dataset.letter;
                this.currentLetter = letter;
            }
        },

        save() {
            this.$dispatch('skills-updated', this.selectedSkills);
            this.open = false;
            this.search = '';
            this.handleSearch({ target: { value: '' } });
        },

        cancel() {
            this.open = false;
            this.search = '';
            this.handleSearch({ target: { value: '' } });
        },

        getVisibleSkillCount() {
            return this.$refs.skillsContainer.querySelectorAll('.skill-card[style*="display: block"], .skill-card:not([style*="display"])').length;
        }
    }));
});
