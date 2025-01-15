document.addEventListener('DOMContentLoaded', function() {
    const parseForm = document.getElementById('parse-form');
    const jobForm = document.getElementById('job-form');
    
    // Handle main form submission
    if (jobForm) {
        jobForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
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

            // Submit form via fetch
            fetch(this.action, {
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
                    showNotification('Success', data.message, 'success');
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
    }

    // Handle AI Parser form
    parseForm.addEventListener('submit', function(evt) {
        evt.preventDefault();
        
        const submitButton = parseForm.querySelector('button[type="submit"]');
        const spinner = submitButton.querySelector('.loading');
        const buttonText = submitButton.querySelector('span:not(.loading)');
        
        // Show loading state
        submitButton.disabled = true;
        spinner.classList.remove('hidden');
        buttonText.textContent = 'Processing...';
        
        const formData = new FormData(this);
        
        fetch(this.getAttribute('hx-post'), {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': formData.get('csrfmiddlewaretoken')
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status === 'success') {
                populateFormFields(data.fields);
                showNotification('Success', 'Form fields populated successfully', 'success');
            } else {
                throw new Error(data.message || 'Failed to parse description');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error', error.message, 'error');
        })
        .finally(() => {
            // Reset button state
            submitButton.disabled = false;
            spinner.classList.add('hidden');
            buttonText.textContent = 'Process with AI';
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
