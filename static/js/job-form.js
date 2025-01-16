document.addEventListener('DOMContentLoaded', function() {
    const parseForm = document.getElementById('parse-form');
    const jobForm = document.getElementById('job-form');
    
    // Handle main form submission
    if (jobForm) {
        console.log('Job form found, attaching submit handler');
        
        jobForm.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('Form submit event triggered');
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const spinner = submitBtn.querySelector('.loading');
            const buttonText = submitBtn.querySelector('.button-text');
            
            // Update button state
            spinner.classList.remove('hidden');
            buttonText.textContent = 'Saving...';
            submitBtn.disabled = true;

            // Prepare form data
            const formData = new FormData(this);
            
            // Add skills if present
            const skillsInput = document.getElementById('skills-input');
            if (skillsInput && skillsInput.value) {
                formData.append('required_skills', skillsInput.value);
            }

            // Log form data for debugging
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
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.status === 'success') {
                    window.location.href = data.redirect_url;
                } else {
                    throw new Error(data.message || 'Form submission failed');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Error', error.message, 'error');
            })
            .finally(() => {
                // Reset button state
                spinner.classList.add('hidden');
                buttonText.textContent = 'Save Job';
                submitBtn.disabled = false;
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

    // Handle AI Parser form response
    document.body.addEventListener('htmx:afterRequest', function(evt) {
        if (evt.detail.elt.id === 'parse-form') {
            const response = evt.detail.xhr.response;
            console.log('HTMX Response:', response);
            
            try {
                let data;
                const contentType = evt.detail.xhr.getResponseHeader('Content-Type');
                
                // Handle different response types
                if (contentType && contentType.includes('application/json')) {
                    // Parse JSON response
                    if (typeof response === 'string') {
                        data = JSON.parse(response);
                    } else {
                        data = response;
                    }
                    
                    if (data.status === 'success') {
                        // Handle both response formats
                        const fields = data.fields || data.data;
                        if (fields) {
                            populateFormFields(fields);
                            showNotification('Success', 'Form fields populated successfully', 'success');
                        } else {
                            throw new Error('No field data found in response');
                        }
                    } else {
                        throw new Error(data.message || 'Failed to parse description');
                    }
                } else if (contentType && contentType.includes('text/html')) {
                    // Handle HTML response (template rendering)
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(response, 'text/html');
                    
                    // Extract field values from the HTML response
                    const fields = {};
                    doc.querySelectorAll('input, textarea').forEach(field => {
                        const name = field.getAttribute('name');
                        if (name) {
                            fields[name] = field.value || field.textContent;
                        }
                    });
                    
                    if (Object.keys(fields).length > 0) {
                        populateFormFields(fields);
                        showNotification('Success', 'Form fields populated successfully', 'success');
                    } else {
                        throw new Error('No fields found in response');
                    }
                } else {
                    throw new Error('Unexpected response type');
                }
            } catch (error) {
                console.error('Error:', error);
                showNotification('Error', error.message, 'error');
                
                // Clear the paste textarea on error
                const pasteArea = document.querySelector('#paste, #id_paste');
                if (pasteArea) {
                    pasteArea.value = '';
                }
            }
            
            // Reset button state
            const submitButton = evt.detail.elt.querySelector('button[type="submit"]');
            const spinner = submitButton.querySelector('.loading');
            const buttonText = submitButton.querySelector('span:not(.loading)');
            
            submitButton.disabled = false;
            spinner.classList.add('hidden');
            buttonText.textContent = 'Process with AI';
        }
    });

    // Log form data being sent
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        if (evt.detail.elt.id === 'parse-form') {
            const formData = new FormData(evt.detail.elt);
            
            // Clean and validate paste text
            let pasteText = formData.get('paste');
            if (!pasteText || pasteText.trim() === '') {
                evt.preventDefault();
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
                .trim();

            // Update the form data with cleaned text
            formData.set('paste', pasteText);

            // Log the cleaned data
            const formDataObj = {};
            formData.forEach((value, key) => {
                formDataObj[key] = value;
            });
            console.log('Cleaned form data being sent:', formDataObj);

            // Update the original event's form data
            evt.detail.requestConfig.body = formData;
        }
    });


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

    // Improved notification function
    function showNotification(title, message, type) {
        if (window.Toastify) {
            Toastify({
                text: message,
                duration: 3000,
                gravity: "top",
                position: "right",
                className: type === 'error' ? 'bg-error' : 'bg-success',
                stopOnFocus: true,
            }).showToast();
        } else {
            console.log(`${title}: ${message} (${type})`);
        }
    }
});
