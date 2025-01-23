class FormHandler {
    constructor() {
        if (window.Alpine) {
            this.init();
        } else {
            document.addEventListener('alpine:init', () => this.init());
        }
        this.debug = true;
    }

    init() {
        this.setupFormHandling();
        this.initializeSkillsModal();
    }

    initializeSkillsModal() {
        if (!window.Alpine) return;

        Alpine.data('skillsModal', () => ({
            open: false,
            selectedSkills: [],
            searchQuery: '',
            filteredSkills: [],

            init() {
                // Get initial skills if any
                const skillsInput = document.getElementById('id_skills');
                if (skillsInput && skillsInput.value) {
                    this.selectedSkills = skillsInput.value.split(',')
                        .map(s => s.trim())
                        .filter(Boolean);
                }

                // Listen for skill updates
                window.addEventListener('skills-updated', (e) => {
                    this.updateSkills(e.detail);
                });
            },

            updateSkills(skills) {
                const skillsInput = document.getElementById('id_skills');
                if (skillsInput) {
                    skillsInput.value = skills.join(',');
                    this.selectedSkills = skills;
                }
            },

            handleSkillSelect(skill) {
                if (!this.selectedSkills.includes(skill)) {
                    this.selectedSkills.push(skill);
                    this.updateSkills(this.selectedSkills);
                }
                this.searchQuery = '';
            },

            removeSkill(skill) {
                this.selectedSkills = this.selectedSkills.filter(s => s !== skill);
                this.updateSkills(this.selectedSkills);
            }
        }));
    }

    setupFormHandling() {
        document.querySelectorAll('form[data-debug]').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });
    }

    handleFormSubmit(event) {
        const form = event.target;
        const submitButton = form.querySelector('[type="submit"]');
        if (!submitButton) return;

        // Show loading state
        const spinner = submitButton.querySelector('.loading-spinner');
        const buttonText = submitButton.querySelector('.button-text');
        if (spinner && buttonText) {
            spinner.classList.remove('hidden');
            buttonText.classList.add('opacity-0');
        }

        // Enable debug logging
        if (this.debug) {
            console.log('Form submitted:', {
                formId: form.id,
                formAction: form.action,
                formMethod: form.method,
                formData: new FormData(form)
            });
        }
    }
}

// Initialize form handler after Alpine.js
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('DOM loaded, waiting for Alpine.js...');
        if (window.Alpine) {
            console.log('Alpine.js loaded, initializing form handler...');
            window.formHandler = new FormHandler();
        } else {
            document.addEventListener('alpine:init', () => {
                console.log('Alpine.js loaded, initializing form handler...');
                window.formHandler = new FormHandler();
            });
        }
    });
} else {
    window.formHandler = new FormHandler();
}
