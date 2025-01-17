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
            
            try {
                const response = await fetch('{% url "jobs:parse" %}', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify({
                        paste: document.getElementById('paste').value
                    })
                });
                
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                
                const data = await response.json();
                
                // Fill the form fields with the parsed data
                if (data.title) document.getElementById('id_title').value = data.title;
                if (data.company) document.getElementById('id_company').value = data.company;
                if (data.location) document.getElementById('id_location').value = data.location;
                if (data.description) document.getElementById('id_description').value = data.description;
                if (data.url) document.getElementById('id_url').value = data.url;
                if (data.salary_range) document.getElementById('id_salary_range').value = data.salary_range;
                
                // Show success message
                window.$store.toastManager.show({
                    type: 'success',
                    message: 'Job details extracted successfully!'
                });
                
            } catch (error) {
                console.error('Error:', error);
                window.$store.toastManager.show({
                    type: 'error',
                    message: 'Failed to process job description'
                });
            } finally {
                // Hide loading state
                spinner.classList.add('hidden');
                this.disabled = false;
            }
        });
    }
});
