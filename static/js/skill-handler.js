class SkillsHandler {
    constructor() {
        this.selectedSkills = [];
        this.filteredSkills = [];
        this.searchQuery = '';
        this.showSuggestions = false;
        this.iconMappings = window.MODAL_ICON_MAPPING || {};
        this.darkVariants = window.MODAL_DARK_VARIANTS || {};
        this.defaultIcon = 'heroicons:academic-cap';
    }

    initSkills(initialSkills = []) {
        this.selectedSkills = initialSkills.map(skill => ({
            name: skill.name,
            icon: this.getIconForSkill(skill.name.toLowerCase()),
            icon_dark: this.getDarkIconForSkill(skill.name.toLowerCase())
        }));
    }

    updateSkills(skills) {
        if (Array.isArray(skills)) {
            this.selectedSkills = skills.map(skill => ({
                name: skill.name,
                icon: this.getIconForSkill(skill.name.toLowerCase()),
                icon_dark: this.getDarkIconForSkill(skill.name.toLowerCase())
            }));
        }
    }

    getIconForSkill(skillName) {
        return this.iconMappings[skillName] || this.defaultIcon;
    }

    getDarkIconForSkill(skillName) {
        const baseIcon = this.getIconForSkill(skillName);
        return this.darkVariants[baseIcon] || baseIcon;
    }

    searchSkills(query) {
        this.searchQuery = query;
        this.showSuggestions = query.length > 0;
        return query ? Object.keys(this.iconMappings).filter(skill =>
            skill.toLowerCase().includes(query.toLowerCase())
        ) : [];
    }

    addSkill(skill) {
        if (!this.selectedSkills.some(s => s.name === skill.name)) {
            this.selectedSkills.push({
                name: skill.name,
                icon: this.getIconForSkill(skill.name.toLowerCase()),
                icon_dark: this.getDarkIconForSkill(skill.name.toLowerCase())
            });
        }
        this.showSuggestions = false;
        this.searchQuery = '';
        return this.selectedSkills;
    }

    removeSkill(skillName) {
        this.selectedSkills = this.selectedSkills.filter(s => s.name !== skillName);
        return this.selectedSkills;
    }

    isSelected(skillName) {
        return this.selectedSkills.some(s => s.name === skillName);
    }

    getSelectedSkills() {
        return this.selectedSkills;
    }

    closeSuggestions() {
        this.showSuggestions = false;
    }
}

// Initialize Alpine.js data
document.addEventListener('alpine:init', () => {
    Alpine.data('skillsHandler', () => new SkillsHandler());
});