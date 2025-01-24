class SkillsManager {
    constructor() {
        this.selectedSkills = new Set();
        this.init();
    }

    init() {
        // Initialize selected skills from hidden input if it exists
        const skillsInput = document.getElementById('id_skills');
        if (skillsInput && skillsInput.value) {
            try {
                const skills = skillsInput.value.split(',')
                    .map(s => s.trim())
                    .filter(Boolean);
                skills.forEach(name => {
                    const skillData = {
                        name,
                        icon: window.MODAL_ICON_MAPPING?.[name.toLowerCase()] || 'heroicons:academic-cap',
                        icon_dark: window.MODAL_DARK_VARIANTS?.[window.MODAL_ICON_MAPPING?.[name.toLowerCase()]] || 'heroicons:academic-cap'
                    };
                    this.selectedSkills.add(JSON.stringify(skillData));
                });
                this.updateSelectedSkillsDisplay();
            } catch (e) {
                console.error('Error parsing initial skills:', e);
            }
        }

        // Listen for skills-updated event
        window.addEventListener('skills-updated', (e) => {
            if (Array.isArray(e.detail)) {
                this.selectedSkills.clear();
                e.detail.forEach(skill => {
                    this.selectedSkills.add(JSON.stringify(skill));
                });
                this.updateSelectedSkillsDisplay();
                this.updateHiddenInput();
            }
        });

        // Listen for skills-restored event
        window.addEventListener('skills-restored', () => {
            this.updateSelectedSkillsDisplay();
        });
    }

    updateHiddenInput() {
        const skillsInput = document.getElementById('id_skills');
        if (skillsInput) {
            const skills = Array.from(this.selectedSkills)
                .map(s => JSON.parse(s))
                .map(s => s.name);
            skillsInput.value = skills.join(',');
            skillsInput.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    updateSelectedSkillsDisplay() {
        const container = document.querySelector('.selected-skills');
        if (!container) return;

        // Clear existing skills
        container.innerHTML = '';
        
        // Show empty state if no skills selected
        if (this.selectedSkills.size === 0) {
            container.innerHTML = '<div class="text-base-content/60 text-sm">Click \'Manage Skills\' to add required skills</div>';
            return;
        }

        // Add each skill badge
        Array.from(this.selectedSkills).forEach(skillString => {
            try {
                const skill = JSON.parse(skillString);
                const badge = document.createElement('div');
                badge.className = 'badge badge-lg gap-2 group relative overflow-hidden p-4 ' +
                    'bg-primary hover:bg-primary/20 ' +
                    'border border-primary/30 hover:border-primary ' +
                    'text-primary-content/90 hover:text-primary-content ' +
                    'transition-all duration-200 ease-in-out ' +
                    'transform hover:scale-105 hover:shadow-md';

                badge.innerHTML = `
                    <div class="w-8 h-8 flex items-center justify-center text-primary group-hover:scale-110 transition-transform duration-200">
                        <iconify-icon icon="${skill.icon_dark || skill.icon || 'heroicons:academic-cap'}"></iconify-icon>
                    </div>
                    <span class="font-medium">${skill.name}</span>
                    <button type="button" 
                            class="ml-1 rounded-full p-1.5 hover:bg-primary/20 active:bg-primary/30
                                   transition-all duration-200 opacity-60 hover:opacity-100"
                            title="Remove skill">
                        <iconify-icon icon="heroicons:x-mark" class="text-sm"></iconify-icon>
                    </button>`;

                // Add click handler for remove button
                const removeButton = badge.querySelector('button');
                removeButton.addEventListener('click', () => {
                    this.selectedSkills.delete(skillString);
                    this.updateSelectedSkillsDisplay();
                    this.updateHiddenInput();
                });

                container.appendChild(badge);
            } catch (e) {
                console.error('Error parsing skill:', e);
            }
        });
    }
}

// Initialize skills manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.skillsManager = new SkillsManager();
});
