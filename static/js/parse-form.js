document.addEventListener('DOMContentLoaded', function() {
    const parseButton = document.getElementById('parse-button');
    const parseForm = document.getElementById('parse-form');
    const mainForm = document.getElementById('job-form');
    
    if (parseButton) {
        parseButton.addEventListener('click', async function(e) {
            e.preventDefault();
            
            // Show loading state
            const spinner = this.querySelector('.loading');
            spinner.classList.remove('hidden');
            this.disabled = true;
            
            const formData = new FormData();
            formData.append('paste', document.getElementById('paste').value);
            
            try {
                const response = await fetch('/jobs/parse-description/', {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                const result = await response.json();
                
                if (result.status === 'error') {
                    throw new Error(result.message);
                }
                
                // Fill the form fields with the parsed data
                const data = result.data;
                if (data.title) document.getElementById('id_title').value = data.title;
                if (data.company) document.getElementById('id_company').value = data.company;
                if (data.location) document.getElementById('id_location').value = data.location;
                if (data.description) document.getElementById('id_description').value = data.description;
                if (data.salary_range) document.getElementById('id_salary_range').value = data.salary_range;
                
                // Show success message
                if (window.$store && window.$store.toastManager) {
                    window.$store.toastManager.show({
                        type: 'success',
                        message: 'Job details extracted successfully!'
                    });
                }
                
            } catch (error) {
                console.error('Error:', error);
                if (window.$store && window.$store.toastManager) {
                    window.$store.toastManager.show({
                        type: 'error',
                        message: error.message || 'Failed to process job description'
                    });
                }
            } finally {
                // Hide loading state
                spinner.classList.add('hidden');
                this.disabled = false;
            }
        });
    }
});
