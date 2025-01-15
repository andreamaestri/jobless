document.addEventListener('DOMContentLoaded', function() {
    const parseForm = document.getElementById('parse-form');
    const jobForm = document.getElementById('job-form');
    const submitBtn = jobForm.querySelector('button[type="submit"]');
    const loadingSpinner = submitBtn.querySelector('.loading');
    
    // Handle main form submission
    jobForm.addEventListener('submit', function(evt) {
        evt.preventDefault();
        
        // Show loading state
        submitBtn.disabled = true;
        loadingSpinner.classList.remove('hidden');
        
        // Collect form data
        const formData = new FormData(this);
        
        // Submit form via fetch
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => {
            if (response.ok) {
                // Redirect to jobs list on success
                window.location.href = '/jobs/';
                showNotification('Success', 'Job saved successfully', 'success');
            } else {
                return response.json().then(data => {
                    throw new Error(data.message || 'Form submission failed');
                });
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error', error.message || 'Failed to save job', 'error');
            
            // Reset button state
            submitBtn.disabled = false;
            loadingSpinner.classList.add('hidden');
        });
    });
    
    // AI Parser form handling
    parseForm.addEventListener('submit', function(evt) {
        evt.preventDefault();
        
        const submitButton = parseForm.querySelector('button[type="submit"]');
        const originalText = submitButton.innerHTML;
        submitButton.disabled = true;
        
        const formData = new FormData(parseForm);
        
        fetch(parseForm.getAttribute('hx-post'), {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                populateFormFields(data.fields);
                showNotification('Success', 'Form fields populated successfully', 'success');
            } else {
                showNotification('Error', data.message || 'Failed to parse description', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error', 'Failed to process response', 'error');
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.innerHTML = originalText;
        });
    });

    // Helper function to populate form fields
    function populateFormFields(fields) {
        Object.entries(fields).forEach(([key, value]) => {
            let field = document.getElementById(`id_${key}`);
            if (!field) {
                field = document.querySelector(`[name="${key}"]`);
            }
            
            if (field) {
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
            }
        });
        
        // Scroll to the form
        jobForm.scrollIntoView({ behavior: 'smooth', block: 'start' });
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
