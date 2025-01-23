// Helper function to wait for Alpine
function waitForAlpine(maxAttempts = 10, interval = 500) {
    return new Promise((resolve, reject) => {
        let attempts = 0;
        const check = () => {
            if (window.Alpine) {
                resolve(window.Alpine);
                return;
            }
            attempts++;
            if (attempts >= maxAttempts) {
                reject(new Error('Alpine.js failed to load'));
                return;
            }
            setTimeout(check, interval);
        };
        check();
    });
}

// Initialize Alpine components
async function initializeAlpineComponents() {
    try {
        const Alpine = await waitForAlpine();
        Alpine.data('skillsModal', () => ({
            open: false,
            search: '',
            selectedSkills: [],
            currentLetter: null,
            touchStartY: null,
            touchStartTime: null,
            currentPreviewLetter: null,
            lastTouchY: null,
            isScrolling: false,
            mouseX: 0,
            mouseY: 0,
            lastMouseX: 0,
            lastMouseY: 0,
            lastSelected: null,
            init() {
                // Initialize selectedSkills as empty array
                this.selectedSkills = [];
                
                // Watch for modal open
                this.$watch('open', value => {
                    if (value) {
                        this.search = '';
                        if (window.skillSelect) {
                            const items = window.skillSelect.items || [];
                            this.selectedSkills = items.map(name => {
                                const option = window.skillSelect.options[name] || {};
                                return {
                                    name: name,
                                    icon: option.icon || 'heroicons:academic-cap',
                                    icon_dark: option.icon_dark
                                };
                            });
                        }
                    }
                });

                // Listen for skills-updated event
                window.addEventListener('skills-updated', (event) => {
                    if (window.skillSelect) {
                        const updatedSkills = event.detail;
                        window.skillSelect.clear(true);
                        window.skillSelect.clearOptions();
                        
                        updatedSkills.forEach(skill => {
                            window.skillSelect.addOption({
                                name: skill.name,
                                icon: skill.icon,
                                icon_dark: skill.icon_dark
                            });
                            window.skillSelect.addItem(skill.name);
                        });

                        // Update hidden input
                        const skillsInput = document.getElementById('skills-input');
                        if (skillsInput) {
                            skillsInput.value = JSON.stringify(updatedSkills);
                        }

                        // Update skills count
                        const skillsCount = document.getElementById('skills-count');
                        if (skillsCount) {
                            skillsCount.textContent = `${updatedSkills.length} selected`;
                        }
                    }
                });
            },

            initializeSkills() {
                try {
                    if (window.skillSelect && window.skillSelect.items) {
                        this.selectedSkills = window.skillSelect.items.map(name => {
                            const option = window.skillSelect.options[name];
                            return {
                                name: option.name,
                                icon: option.icon,
                                icon_dark: option.icon_dark
                            };
                        });
                    }
                } catch (error) {
                    console.error('Error initializing skills:', error);
                    this.selectedSkills = [];
                }
            },

            toggleSkill(skill) {
                try {
                    const index = this.selectedSkills.findIndex(s => s.name === skill.name);
                    if (index === -1) {
                        this.selectedSkills.push({ ...skill });
                    } else {
                        this.selectedSkills.splice(index, 1);
                    }
                } catch (error) {
                    console.error('Error toggling skill:', error);
                }
            },

            save() {
                const skillsToUpdate = this.selectedSkills.map(skill => ({
                    name: skill.name,
                    icon: skill.icon,
                    icon_dark: skill.icon_dark
                }));
            
                // Update hidden input
                const skillsInput = document.getElementById('skills-input');
                if (skillsInput) {
                    skillsInput.value = JSON.stringify(skillsToUpdate);
                }

                window.dispatchEvent(new CustomEvent('skills-updated', {
                    detail: skillsToUpdate
                }));
            
                // Update TomSelect directly
                if (window.skillSelect) {
                    window.skillSelect.clear(true);
                    window.skillSelect.clearOptions();
                
                    skillsToUpdate.forEach(skill => {
                        window.skillSelect.addOption({
                            name: skill.name,
                            icon: skill.icon,
                            icon_dark: skill.icon_dark
                        });
                        window.skillSelect.addItem(skill.name);
                    });
                }
            
                this.updateSelectedSkillsDisplay();
                this.open = false;
            },

            updateSelectedSkillsDisplay() {
                const container = document.querySelector('.selected-skills-container');
                if (!container) return;

                // Clear existing skills
                while (container.firstChild) {
                    container.removeChild(container.firstChild);
                }

                // Show empty state if no skills selected
                if (this.selectedSkills.length === 0) {
                    container.innerHTML = '<div class="text-base-content/60 text-sm">Click \'Manage Skills\' to add required skills</div>';
                    return;
                }

                // Add each skill badge
                this.selectedSkills.forEach(skill => {
                    const badge = document.createElement('div');
                    badge.className = 'badge badge-lg gap-2 group relative overflow-hidden p-4 ' +
                                    'bg-primary hover:bg-primary/20 ' +
                                    'border border-primary/30 hover:border-primary ' +
                                    'text-primary-content/90 hover:text-primary-content ' +
                                    'transition-all duration-200 ease-in-out ' +
                                    'transform hover:scale-105 hover:shadow-md';
                
                    badge.innerHTML = `
                        <div class="w-8 h-8 flex items-center justify-center text-primary group-hover:scale-110 transition-transform duration-200">
                            <iconify-icon icon="${skill.icon_dark || skill.icon || 'heroicons:academic-cap'}"></iconify-icon>
                        </div>
                        <span class="font-medium">${skill.name}</span>
                    `;
                    container.appendChild(badge);
                });
            },

            resetModalState() {
                this.search = '';
                window.skillsManager?.resetModalState();
            },

            isSelected(skillName) {
                return this.selectedSkills.some(s => s.name === skillName);
            },

            handleSearch(event) {
                const searchTerm = event.target.value.toLowerCase();
                document.querySelectorAll('.skill-group').forEach(group => {
                    let hasVisible = false;
                    group.querySelectorAll('.skill-card').forEach(card => {
                        const name = card.querySelector('.skill-name').textContent.toLowerCase();
                        const visible = !searchTerm || name.includes(searchTerm);
                        card.style.display = visible ? '' : 'none';
                        if (visible) hasVisible = true;
                    });
                    group.style.display = hasVisible ? '' : 'none';
                });
            }
        }));
    } catch (error) {
        console.error('Failed to initialize Alpine components:', error);
    }
}

// Start initialization
initializeAlpineComponents();

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
