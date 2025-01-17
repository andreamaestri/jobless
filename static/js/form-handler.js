class FormHandler {
    constructor() {
        this.init();
    }

    init() {
        this.jobForm = document.getElementById('job-form');
        this.parseForm = document.getElementById('parse-form');
        this.parseButton = document.getElementById('parse-button');
        
        if (this.jobForm) {
            this.jobForm.addEventListener('submit', this.handleJobSubmit.bind(this));
        }
        
        if (this.parseButton) {
            this.parseButton.addEventListener('click', this.handleParse.bind(this));
        }
    }

    async handleJobSubmit(e) {
        e.preventDefault();
        
        if (!this.validateForm()) return;

        const actionBtn = document.querySelector('.form-actions button.btn-primary');
        if (!actionBtn) return;

        this.setButtonState(actionBtn, true, 'Saving...');

        try {
            const formData = new FormData(this.jobForm);
            const skillsInput = document.getElementById('skills-input');
            if (skillsInput?.value) {
                formData.append('required_skills', skillsInput.value);
            }

            const response = await this.submitForm(this.jobForm.action, formData);
            
            if (response.status === 'success') {
                window.location.href = response.redirect_url;
            } else {
                this.handleErrors(response);
            }
        } catch (error) {
            this.showNotification('Error', error.message || 'Failed to save job', 'error');
        } finally {
            this.setButtonState(actionBtn, false, 'Save Job');
        }
    }

    async handleParse(e) {
        e.preventDefault();
        
        const pasteText = document.getElementById('paste')?.value?.trim();
        if (!pasteText) {
            this.showNotification('Error', 'Please paste a job description first', 'error');
            return;
        }

        const cleanedText = this.cleanText(pasteText);
        const formData = new FormData();
        formData.append('paste', cleanedText);
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        this.setButtonState(this.parseButton, true, 'Processing...');

        try {
            const response = await this.submitForm('/jobs/parse-description/', formData);
            
            if (response.status === 'success' && response.data) {
                this.populateFormFields(response.data);
                this.showNotification('Success', 'Job details extracted successfully!', 'success');
                document.getElementById('paste').value = '';
            } else {
                throw new Error(response.message || 'Failed to parse description');
            }
        } catch (error) {
            this.showNotification('Error', error.message, 'error');
        } finally {
            this.setButtonState(this.parseButton, false, 'Process with AI');
        }
    }

    validateForm() {
        const requiredFields = this.jobForm.querySelectorAll('[required]');
        let firstInvalidField = null;
        let missingFields = [];

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('input-error');
                if (!firstInvalidField) firstInvalidField = field;
                const label = document.querySelector(`label[for="${field.id}"]`);
                if (label) {
                    missingFields.push(label.textContent.replace(' *', '').trim());
                }
            } else {
                field.classList.remove('input-error');
            }
        });

        if (missingFields.length > 0) {
            this.showNotification('Error', `Please fill in required fields: ${missingFields.join(', ')}`, 'error');
            firstInvalidField?.scrollIntoView({ behavior: 'smooth', block: 'center' });
            firstInvalidField?.focus();
            return false;
        }
        return true;
    }

    async submitForm(url, formData) {
        const response = await fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        });

        const data = await response.json();
        
        if (!response.ok) {
            if (data.errors) return data;
            throw new Error(data.message || 'Server error occurred');
        }
        
        return data;
    }

    handleErrors(data) {
        if (data.errors) {
            const errorMessages = [];
            Object.entries(data.errors).forEach(([field, errors]) => {
                const fieldElement = document.getElementById(`id_${field}`);
                if (fieldElement) {
                    fieldElement.classList.add('input-error');
                    errorMessages.push(`${field}: ${errors.join(', ')}`);
                }
            });
            
            if (errorMessages.length > 0) {
                this.showNotification('Error', errorMessages.join('\n'), 'error');
                const firstErrorField = document.querySelector('.input-error');
                if (firstErrorField) {
                    firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstErrorField.focus();
                }
            }
        } else {
            throw new Error(data.message || 'Form submission failed');
        }
    }

    setButtonState(button, loading, text) {
        const spinner = button.querySelector('.loading');
        const buttonText = button.querySelector('.button-text') || button.querySelector('span:not(.loading)');
        
        button.disabled = loading;
        if (spinner) spinner.classList.toggle('hidden', !loading);
        if (buttonText) buttonText.textContent = text;
    }

    populateFormFields(fields) {
        const fieldMap = {
            title: 'id_title',
            company: 'id_company',
            location: 'id_location',
            url: 'id_url',
            salary_range: 'id_salary_range',
            description: 'id_description',
            status: 'id_status'
        };

        Object.entries(fields).forEach(([key, value]) => {
            const field = document.getElementById(fieldMap[key] || `id_${key}`) 
                      || document.querySelector(`[name="${key}"]`);
            
            if (field) {
                field.value = value;
                
                if (field.tagName === 'TEXTAREA') {
                    field.style.height = 'auto';
                    field.style.height = field.scrollHeight + 'px';
                }
                
                field.dispatchEvent(new Event('input', { bubbles: true }));
                field.dispatchEvent(new Event('change', { bubbles: true }));
            }
        });
        
        this.jobForm?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    cleanText(text) {
        return text.trim()
            .replace(/[\u2018\u2019]/g, "'")
            .replace(/[\u201C\u201D]/g, '"')
            .replace(/\r\n/g, '\n')
            .replace(/\r/g, '\n')
            .replace(/[^\x20-\x7E\n]/g, ' ')
            .replace(/\s+/g, ' ')
            .replace(/^[•\-]\s*/gm, '')
            .trim();
    }

    showNotification(title, message, type) {
        const toastManager = window.$store?.toastManager;
        if (toastManager) {
            toastManager.show({
                type: type,
                message: message,
                description: title !== message ? title : ''
            });
        }
    }
}

// Initialize form handler when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.formHandler = new FormHandler();
});
