class FormHandler {
    constructor() {
        this.init();
        this.debug = true; // Enable debugging
    }

    init() {
        console.log('FormHandler initializing...');
        this.jobForm = document.getElementById('job-form');
        this.parseForm = document.getElementById('description-parser');
        this.parseButton = document.getElementById('parse-button');
        
        console.log('Forms found:', {
            jobForm: !!this.jobForm,
            parseForm: !!this.parseForm,
            parseButton: !!this.parseButton
        });

        if (this.jobForm) {
            this.jobForm.addEventListener('submit', this.handleJobSubmit.bind(this));
        }

        if (this.parseForm) {
            console.log('Adding parser form submit handler');
            this.parseButton.addEventListener('click', (e) => {
                console.log('Parse button clicked');
                e.preventDefault();
                e.stopPropagation();
                this.handleParse(e);
            });
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
                // Parse skills to remove duplicates
                const skills = JSON.parse(skillsInput.value);
                const uniqueSkills = Array.from(new Set(skills.map(s => JSON.stringify(s))))
                    .map(s => JSON.parse(s));
                formData.set('skills', JSON.stringify(uniqueSkills));
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
        console.log('handleParse called');
        e.preventDefault();
        e.stopPropagation();
        
        if (!this.parseForm) {
            console.error('Parser form not found');
            this.showNotification('Error', 'Parse form not found', 'error');
            return;
        }

        const description = this.parseForm.querySelector('#paste')?.value?.trim();
        console.log('Description:', description?.substring(0, 100) + '...');
        
        if (!description) {
            console.warn('No description provided');
            this.showNotification('Error', 'Please paste a job description first', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('description', this.cleanText(description));
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        const submitButton = this.parseButton;
        console.log('Submit button:', submitButton);
        this.setButtonState(submitButton, true, 'Processing...');

        try {
            const parseUrl = this.parseForm.dataset.url;
            console.log('Sending request to:', parseUrl);
            const response = await fetch(parseUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);
            
            if (!response.ok) {
                throw new Error(data.message || data.error || 'Server error occurred');
            }

            if (data.status === 'success' && data.data) {
                console.log('Successfully parsed job data');
                this.populateFormFields(data.data);
                this.showNotification('Success', 'Job details extracted successfully!', 'success');
                this.parseForm.querySelector('#paste').value = '';
            } else {
                throw new Error(data.message || data.error || 'Failed to parse description');
            }
        } catch (error) {
            console.error('Parse error:', error);
            this.showNotification('Error', error.message || 'Failed to process job description', 'error');
        } finally {
            this.setButtonState(submitButton, false, 'Process with AI');
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
        console.log('Populating form fields:', fields);
        
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
            if (!value) return; // Skip empty values
            
            const fieldId = fieldMap[key];
            console.log(`Setting ${key} (${fieldId}) to:`, value.substring(0, 50) + '...');
            
            const field = document.getElementById(fieldId) || 
                         document.querySelector(`[data-field="${key}"]`);
            if (!field) {
                console.warn(`Field not found: ${fieldId} or data-field="${key}"`);
                return;
            }
            
            field.value = value;
            
            if (field.tagName === 'TEXTAREA') {
                field.style.height = 'auto';
                field.style.height = field.scrollHeight + 'px';
            }
            
            field.dispatchEvent(new Event('input', { bubbles: true }));
            field.dispatchEvent(new Event('change', { bubbles: true }));
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
        if (window.Alpine && Alpine.store('toastManager')) {
            Alpine.store('toastManager').show({
                type: type,
                message: message,
                description: title !== message ? title : ''
            });
        } else {
            console.warn('Toast manager not available');
        }
    }
}

// Add this outside the class to debug form availability
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, checking form elements...');
    const descriptionParser = document.getElementById('description-parser');
    console.log('Description parser form found:', !!descriptionParser);
    
    // Initialize form handler
    window.formHandler = new FormHandler();
});
