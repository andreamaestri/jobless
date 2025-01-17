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
                
                const data = await response.json();
                
                if (data.status === 'error') {
                    throw new Error(data.message || 'Failed to parse job description');
                }
                
                // Fill the form fields with the parsed data
                const result = data.data;
                if (result.title) document.getElementById('id_title').value = result.title;
                if (result.company) document.getElementById('id_company').value = result.company;
                if (result.location) document.getElementById('id_location').value = result.location;
                if (result.description) document.getElementById('id_description').value = result.description;
                if (result.salary_range) document.getElementById('id_salary_range').value = result.salary_range;
                
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
