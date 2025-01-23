class FormHandler {
    constructor() {
        // Wait for Alpine.js to be ready
        if (window.Alpine) {
            this.init();
        } else {
            document.addEventListener('alpine:init', () => this.init());
        }
        this.debug = true;
    }

    init() {
        this.setupFormHandling();
        this.setupSkillsHandling();
    }

    setupFormHandling() {
        document.querySelectorAll('form[data-debug]').forEach(form => {
            form.addEventListener('submit', this.handleFormSubmit.bind(this));
        });
    }

    setupSkillsHandling() {
        // Initialize Alpine.js data for skills
        if (window.Alpine) {
            Alpine.data('skillsData', () => ({
                selectedSkills: [],
                updateSkills(skills) {
                    this.selectedSkills = skills;
                    document.dispatchEvent(new CustomEvent('skills-updated', {
                        detail: skills
                    }));
                }
            }));
        }
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
