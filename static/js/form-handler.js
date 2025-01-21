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
        this.descriptionField = document.getElementById('id_description');
        this.charCounter = document.getElementById('char-counter');
        
        console.log('Forms found:', {
            jobForm: !!this.jobForm,
            parseForm: !!this.parseForm,
            parseButton: !!this.parseButton,
            descriptionField: !!this.descriptionField,
            charCounter: !!this.charCounter
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

        if (this.descriptionField && this.charCounter) {
            this.descriptionField.addEventListener('input', () => {
                const count = this.descriptionField.value.length;
                this.charCounter.textContent = `${count}/4000`;
                this.charCounter.classList.toggle('text-error', count > 4000);
            });
            // Initialize counter
            this.descriptionField.dispatchEvent(new Event('input'));
        }
    }

    async handleJobSubmit(e) {
        e.preventDefault();
        e.stopPropagation();
        
        if (!this.validateForm()) return;

        const actionBtn = document.querySelector('button[type="submit"][form="job-form"]');
        if (!actionBtn) {
            console.error('Submit button not found');
            return;
        }

        this.setButtonState(actionBtn, true, 'Saving...');

        try {
            const formData = new FormData(this.jobForm);
            
            // Process skills input
            const skillsInput = document.getElementById('skills-input');
            if (skillsInput && skillsInput.value) {
                try {
                    const skills = JSON.parse(skillsInput.value);
                    // Extract just the names and join with commas
                    const skillNames = skills.map(s => s.name.toLowerCase()).join(',');
                    console.log('Processing skills:', { raw: skills, formatted: skillNames });
                    formData.set('skills', skillNames);
                } catch (e) {
                    console.error('Error processing skills:', e);
                    this.showNotification('Error', 'Invalid skills data format', 'error');
                    return;
                }
            }

            const response = await this.submitForm(this.jobForm.action, formData);
            
            if (response.status === 'success') {
                window.location.href = response.redirect_url;
            } else {
                this.handleErrors(response);
            }
        } catch (error) {
            console.error('Form submission error:', error);
            this.showNotification('Error', error.message || 'Failed to save job', 'error');
        } finally {
            this.setButtonState(actionBtn, false, 'Save Job');
        }
    }

    async handleParse(e) {
        console.log('handleParse called');
        e.preventDefault();
        e.stopPropagation();
        
        const descriptionInput = this.parseForm.querySelector('#paste');
        if (!descriptionInput) {
            console.error('Description input not found');
            this.showNotification('Error', 'Form configuration error', 'error');
            return;
        }

        const description = descriptionInput.value?.trim();
        if (!description) {
            this.showNotification('Error', 'Please paste a job description first', 'error');
            descriptionInput.focus();
            return;
        }

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) {
            console.error('CSRF token not found');
            this.showNotification('Error', 'Security token missing', 'error');
            return;
        }

        const parseUrl = this.parseForm.dataset.url;
        if (!parseUrl) {
            console.error('Parse URL not found in data attribute');
            this.showNotification('Error', 'Configuration error', 'error');
            return;
        }

        const submitButton = this.parseButton;
        const errorDiv = document.getElementById('parse-error');
        
        this.setButtonState(submitButton, true, 'Processing...');
        if (errorDiv) errorDiv.classList.add('hidden');

        try {
            const formData = new FormData();
            formData.append('description', this.cleanText(description));
            formData.append('csrfmiddlewaretoken', csrfToken);

            const response = await fetch(parseUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrfToken
                }
            });

            const data = await response.json();
            
            if (!response.ok) {
                let errorMessage = data.error || 'Failed to parse description';
                
                // Handle missing fields specifically
                if (data.missing_fields && data.missing_fields.length > 0) {
                    errorMessage = `AI couldn't extract these fields: ${data.missing_fields.join(', ')}. Please fill them manually.`;
                }
                
                // Show error in both notification and error div
                this.showNotification('Error', errorMessage, 'error');
                if (errorDiv) {
                    errorDiv.textContent = errorMessage;
                    errorDiv.classList.remove('hidden');
                }
                return;
            }

            if (data.status === 'success' && data.data) {
                this.populateFormFields(data.data);
                this.showNotification('Success', 'Job details extracted successfully!', 'success');
                descriptionInput.value = '';
                if (errorDiv) errorDiv.classList.add('hidden');
            } else {
                throw new Error(data.error || 'No data returned from parser');
            }
        } catch (error) {
            console.error('Parse error:', error);
            const errorMessage = error.message || 'Failed to process job description. Please try again.';
            this.showNotification('Error', errorMessage, 'error');
            if (errorDiv) {
                errorDiv.textContent = errorMessage;
                errorDiv.classList.remove('hidden');
            }
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
        try {
            console.log('Submitting form to:', url);
            const response = await fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            });

            const data = await response.json();
            console.log('Form submission response:', data);
            
            if (!response.ok) {
                if (data.errors) return data;
                throw new Error(data.message || `Server error: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('Form submission error:', error);
            throw error;
        }
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
