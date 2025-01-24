import Alpine from 'alpinejs'
import 'iconify-icon'

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

// Export FormHandler class
export default FormHandler;