class SkillsManager {
    constructor() {
        this.selectedSkills = new Set();
        this.init();
    }

    init() {
        // Initialize selected skills from hidden input if it exists
        const skillsInput = document.getElementById('skills-input');
        if (skillsInput && skillsInput.value) {
            try {
                const skills = JSON.parse(skillsInput.value);
                skills.forEach(skill => this.selectedSkills.add(JSON.stringify(skill)));
                this.updateSelectedSkillsDisplay();
            } catch (e) {
                console.error('Error parsing initial skills:', e);
            }
        }

        // Initialize search functionality
        const searchInput = document.getElementById('skill-search');
        if (searchInput) {
            searchInput.addEventListener('input', this.handleSearch.bind(this));
        }

        // Initialize quick letter navigation
        const letterButtons = document.querySelectorAll('.quick-letter');
        letterButtons.forEach(button => {
            button.addEventListener('click', () => {
                const letter = button.dataset.letter;
                const group = document.querySelector(`.skill-group[data-letter="${letter}"]`);
                if (group) {
                    group.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });

        // Initialize checkbox handlers
        const checkboxes = document.querySelectorAll('input[type="checkbox"][data-skill]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                const skillData = checkbox.dataset.skill;
                if (checkbox.checked) {
                    this.selectedSkills.add(skillData);
                } else {
                    this.selectedSkills.delete(skillData);
                }
            });
        });
    }

    handleSearch(event) {
        const searchTerm = event.target.value.toLowerCase();
        const labels = document.querySelectorAll('.skill-group label');
        
        labels.forEach(label => {
            const skillName = label.querySelector('span').textContent.toLowerCase();
            if (skillName.includes(searchTerm)) {
                label.style.display = '';
            } else {
                label.style.display = 'none';
            }
        });
    }

    updateSelectedSkillsDisplay() {
        const container = document.getElementById('selected-skills');
        const emptyState = document.querySelector('.empty-state');
        
        if (!container || !emptyState) return;

        container.innerHTML = '';
        
        if (this.selectedSkills.size === 0) {
            emptyState.style.display = 'flex';
            return;
        }

        emptyState.style.display = 'none';
        
        Array.from(this.selectedSkills).forEach(skillString => {
            try {
                const skill = JSON.parse(skillString);
                const badge = document.createElement('div');
                badge.className = 'badge badge-lg gap-2 badge-primary';
                badge.innerHTML = `
                    <iconify-icon icon="${skill.icon}" style="font-size: 1.2em;"></iconify-icon>
                    <span>${skill.name}</span>
                `;
                container.appendChild(badge);
            } catch (e) {
                console.error('Error parsing skill:', e);
            }
        });
    }

    applySelectedSkills() {
        const skillsInput = document.getElementById('skills-input');
        if (skillsInput) {
            // Remove duplicates before saving
            const uniqueSkills = Array.from(new Set(Array.from(this.selectedSkills)))
                .map(s => JSON.parse(s));
            skillsInput.value = JSON.stringify(uniqueSkills);
        }
        this.updateSelectedSkillsDisplay();
    }

    resetModalState() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"][data-skill]');
        checkboxes.forEach(checkbox => {
            const skillData = checkbox.dataset.skill;
            checkbox.checked = this.selectedSkills.has(skillData);
        });

        const searchInput = document.getElementById('skill-search');
        if (searchInput) {
            searchInput.value = '';
            searchInput.dispatchEvent(new Event('input'));
        }
    }
}

// Initialize skills manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.skillsManager = new SkillsManager();
});

if (window.Alpine) {
    window.Alpine.data('skillsModal', () => ({
        open: false,
        selectedSkills: [],
        search: '',
        currentLetter: null,
        
        init() {
            this.$watch('open', value => {
                if (!value) {
                    this.search = '';
                    window.skillsManager?.resetModalState();
                }
            });
            // Initialize with current TomSelect selections
            if (window.skillSelect) {
                this.selectedSkills = window.skillSelect.items.map(name => {
                    const option = window.skillSelect.options[name];
                    return {
                        name: option.name,
                        icon: option.icon,
                        icon_dark: option.icon_dark
                    };
                });
            }
        },

        toggleSkill(skill) {
            const index = this.selectedSkills.findIndex(s => s.name === skill.name);
            if (index === -1) {
                this.selectedSkills.push(skill);
            } else {
                this.selectedSkills.splice(index, 1);
            }
        },

        saveSkills() {
            // Dispatch event for TomSelect to handle
            this.$dispatch('skills-updated', this.selectedSkills);
            this.open = false;
        },

        isSelected(skillName) {
            return this.selectedSkills.some(s => s.name === skillName);
        }
    }));
});
