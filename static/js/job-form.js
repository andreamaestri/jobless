console.log('job-form.js loaded');
try {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('DOMContentLoaded event fired');
    const parseForm = document.getElementById('parse-form');
    const jobForm = document.getElementById('job-form');
    
    // Handle main form submission
    console.log('Checking for job form...');
    if (jobForm) {
        console.log('Job form found:', jobForm);
        console.log('Attaching submit handler...');
        
        // Log all buttons in the form for debugging
        const allButtons = jobForm.querySelectorAll('button');
        console.log('All buttons in form:', Array.from(allButtons).map(btn => ({
            type: btn.type,
            classes: btn.className,
            text: btn.textContent.trim()
        })));
        
        jobForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submit event triggered');
            
            // Get all required fields
            const requiredFields = this.querySelectorAll('[required]');
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
                console.error('Form validation failed');
                const message = `Please fill in required fields: ${missingFields.join(', ')}`;
                console.log('Showing notification:', message);
                
                // Use Alpine.js toast system
                const toastManager = Alpine.store('toastManager');
                if (toastManager) {
                    toastManager.addToast({
                        id: Date.now(),
                        message: message,
                        type: 'error',
                        progress: 100
                    });
                }

                if (firstInvalidField) {
                    firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    firstInvalidField.focus();
                }
                return;
            }

            // Find the visible action button
            const actionBtn = document.querySelector('.form-actions button.btn-primary');
            if (!actionBtn) {
                console.error('Action button not found');
                return;
            }

            // Get spinner and text elements
            const spinner = actionBtn.querySelector('.loading');
            const buttonText = actionBtn.querySelector('.button-text');

            // Update button state
            if (spinner) spinner.classList.remove('hidden');
            if (buttonText) buttonText.textContent = 'Saving...';
            actionBtn.disabled = true;

            // Prepare form data
            const formData = new FormData(this);
            
            // Add skills if present
            const skillsInput = document.getElementById('skills-input');
            if (skillsInput && skillsInput.value) {
                formData.append('required_skills', skillsInput.value);
            }

            // Debug log form data
            console.log('Form data being submitted:');
            for (let pair of formData.entries()) {
                console.log(pair[0] + ': ' + pair[1]);
            }

            // Submit form via fetch
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                },
                credentials: 'same-origin'
            })
            .then(async response => {
                const contentType = response.headers.get('content-type');
                const data = await response.json();
                
                // If response is not ok, but we have JSON data with errors
                if (!response.ok && data.errors) {
                    return data;
                }
                
                // If response is not ok and no error data
                if (!response.ok) {
                    throw new Error(data.message || 'Server error occurred');
                }
                
                return data;
            })
            .then(data => {
                console.log('Server response:', data);
                if (data.status === 'success') {
                    window.location.href = data.redirect_url;
                } else {
                    // Handle validation errors
                    if (data.errors) {
                        const errorMessages = [];
                        Object.entries(data.errors).forEach(([field, errors]) => {
                            // Find the field element
                            const fieldElement = document.getElementById(`id_${field}`);
                            if (fieldElement) {
                                fieldElement.classList.add('input-error');
                                errorMessages.push(`${field}: ${errors.join(', ')}`);
                            }
                        });
                        
                        // Show error messages in toast
                        if (errorMessages.length > 0) {
                            showNotification('Error', errorMessages.join('\n'), 'error');
                            
                            // Scroll to first error field
                            const firstErrorField = document.querySelector('.input-error');
                            if (firstErrorField) {
                                firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                firstErrorField.focus();
                            }
                        } else {
                            showNotification('Error', data.message || 'Please correct the errors below', 'error');
                        }
                    } else {
                        throw new Error(data.message || 'Form submission failed');
                    }
                }
            })
            .catch(error => {
                console.error('Error during form submission:', error);
                if (error.message) {
                    showNotification('Error', error.message, 'error');
                } else {
                    showNotification('Error', 'Failed to save job. Please try again.', 'error');
                }
            })
            .finally(() => {
                // Reset button state
                if (spinner) spinner.classList.add('hidden');
                if (buttonText) buttonText.textContent = 'Save Job';
                actionBtn.disabled = false;
            });
        });
    } else {
        console.warn('Job form not found');
    }

    // Get CSRF token from cookie
    function getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Handle parse form submission
    if (parseForm) {
        parseForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Get form data
            const formData = new FormData(this);
            
            // Clean and validate paste text
            let pasteText = formData.get('paste');
            if (!pasteText || pasteText.trim() === '') {
                showNotification('Error', 'Please paste a job description first', 'error');
                return;
            }

            // Clean the text
            pasteText = pasteText.trim()
                .replace(/[\u2018\u2019]/g, "'")   // Smart quotes
                .replace(/[\u201C\u201D]/g, '"')   // Smart quotes
                .replace(/\r\n/g, '\n')            // Normalize line endings
                .replace(/\r/g, '\n')              // Normalize line endings
                .replace(/[^\x20-\x7E\n]/g, ' ')   // Remove non-printable chars
                .replace(/\s+/g, ' ')              // Normalize whitespace
                .replace(/^[•\-]\s*/gm, '')        // Remove bullet points and dashes at start of lines
                .trim();

            formData.set('paste', pasteText);

            // Show loading state
            const submitButton = this.querySelector('button[type="submit"]');
            const spinner = submitButton.querySelector('.loading');
            const buttonText = submitButton.querySelector('span:not(.loading)');
            
            submitButton.disabled = true;
            spinner.classList.remove('hidden');
            buttonText.textContent = 'Processing...';

            // Submit form via fetch
            fetch('/jobs/parse-description/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(async response => {
                const data = await response.json();
                
                // If response is not ok, but we have JSON data with errors
                if (!response.ok && data.errors) {
                    return data;
                }
                
                // If response is not ok and no error data
                if (!response.ok) {
                    throw new Error(data.message || 'Server error occurred');
                }
                
                return data;
            })
            .then(data => {
                if (data.status === 'success' && data.data) {
                    populateFormFields(data.data);
                    showNotification('Success', 'Form fields populated successfully', 'success');
                } else {
                    throw new Error(data.message || 'Failed to parse description');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error', error.message, 'error');
                
                // Clear the paste textarea on error
                const pasteArea = document.querySelector('#paste, #id_paste');
                if (pasteArea) {
                    pasteArea.value = '';
                }
            })
            .finally(() => {
                // Reset button state
                submitButton.disabled = false;
                spinner.classList.add('hidden');
                buttonText.textContent = 'Process with AI';
            });
        });
    }


    // Helper function to populate form fields
    function populateFormFields(fields) {
        console.log('Populating fields with:', fields);
        
        // Map of field names to form IDs
        const fieldMap = {
            'title': 'id_title',
            'company': 'id_company',
            'location': 'id_location',
            'url': 'id_url',
            'salary_range': 'id_salary_range',
            'description': 'id_description',
            'status': 'id_status'
        };

        Object.entries(fields).forEach(([key, value]) => {
            // Try both mapped ID and original key
            const fieldId = fieldMap[key] || `id_${key}`;
            let field = document.getElementById(fieldId);
            
            if (!field) {
                field = document.querySelector(`[name="${key}"]`);
            }
            
            if (field) {
                console.log(`Setting ${key} to:`, value);
                
                // Set the value
                field.value = value;
                
                // Handle textareas
                if (field.tagName === 'TEXTAREA') {
                    field.style.height = 'auto';
                    field.style.height = field.scrollHeight + 'px';
                }
                
                // Trigger input event for all fields
                field.dispatchEvent(new Event('input', { bubbles: true }));
                field.dispatchEvent(new Event('change', { bubbles: true }));
            } else {
                console.warn(`Field not found for ${key}`);
            }
        });
        
        // Scroll to the form
        jobForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
        
        // Clear the paste textarea after successful population
        const pasteArea = document.querySelector('#paste, #id_paste');
        if (pasteArea) {
            pasteArea.value = '';
        }
    }

    // Show notification using toast system
    function showNotification(title, message, type) {
        // Initialize if needed
        if (!window.ToastSystem) {
            console.error('Toast system not found');
            return;
        }
        
        // Show the toast
        window.ToastSystem.show(message, type);
    }
    });
} catch (error) {
    console.error('Error in job-form.js:', error);
}
