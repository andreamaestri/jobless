document.addEventListener('DOMContentLoaded', function() {
    function setupSkillSelects() {
        document.querySelectorAll('.skill-select').forEach(select => {
            select.addEventListener('change', function() {
                const selectedOption = this.options[this.selectedIndex];
                const row = this.closest('tr');
                const icon = selectedOption.getAttribute('data-icon') || 'heroicons:academic-cap';
                
                let iconElement = row.querySelector('iconify-icon');
                if (!iconElement) {
                    iconElement = document.createElement('iconify-icon');
                    iconElement.setAttribute('width', '20');
                    iconElement.setAttribute('height', '20');
                    this.parentNode.insertBefore(iconElement, this);
                }
                iconElement.setAttribute('icon', icon);
            });
        });
    }

    setupSkillSelects();
    document.querySelector('.add-row a').addEventListener('click', function() {
        setTimeout(setupSkillSelects, 100);
    });
});
