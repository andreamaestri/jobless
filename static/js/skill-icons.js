class SkillIconsHelper {
    constructor() {
        this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.watchThemeChanges();
        this.cachedIconStatuses = new Map(); // Cache for icon existence checks
    }

    watchThemeChanges() {
        // Watch for theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            this.darkMode = e.matches;
            this.updateIcons();
        });
    }

    async validateIcon(iconName) {
        if (this.cachedIconStatuses.has(iconName)) {
            return this.cachedIconStatuses.get(iconName);
        }

        try {
            const exists = await window.Iconify.loadIcon(iconName);
            this.cachedIconStatuses.set(iconName, !!exists);
            return !!exists;
        } catch (e) {
            this.cachedIconStatuses.set(iconName, false);
            return false;
        }
    }

    getIconVariant(iconData) {
        if (!iconData) return null;
        const icon = this.darkMode && iconData.icon_dark ? iconData.icon_dark : iconData.icon;
        return icon.trim();
    }

    async updateIcons() {
        const elements = document.querySelectorAll('[data-skill-icon]');
        for (const element of elements) {
            const iconData = JSON.parse(element.getAttribute('data-skill-icon'));
            const iconify = element.querySelector('.iconify');
            if (iconify) {
                const icon = this.getIconVariant(iconData);
                if (await this.validateIcon(icon)) {
                    iconify.setAttribute('data-icon', icon);
                } else {
                    iconify.setAttribute('data-icon', 'octicon:code-16');
                }
            }
        }
    }
}

// Initialize skills helper when page loads
window.skillsHelper = {
    _skills: [],
    _initialized: false,

    async initialize() {
        if (this._initialized) {
            // Always refresh icons if we've already initialized before
            this.updateIcons();
            return;
        }
        try {
            const response = await fetch('/jobs/api/skills/');
            if (!response.ok) throw new Error('Failed to load skills data');
            this._skills = await response.json();
            this._initialized = true;
            this.updateIcons();
        } catch (error) {
            console.error('Failed to initialize skills:', error);
        }
    },

    updateIcons() {
        // Update all skill icons in the document
        document.querySelectorAll('[data-skill-icon]').forEach(element => {
            const iconData = JSON.parse(element.getAttribute('data-skill-icon'));
            const iconify = element.querySelector('.iconify');
            if (iconify) {
                const icon = this.getIconByName(iconData.name);
                iconify.setAttribute('data-icon', icon);
            }
        });
    },

    getIconByName(skillName) {
        const skill = this._skills.find(s => s.text === skillName);
        if (!skill) return 'octicon:code-16';
        return skill.icon;
    },

    getCategories() {
        return [...new Set(this._skills.map(skill => skill.icon.split(':')[0]))];
    },

    filterByCategory(category) {
        return category 
            ? this._skills.filter(skill => skill.icon.startsWith(category + ':'))
            : this._skills;
    },

    searchSkills(query) {
        if (!query) return this._skills;
        const lowerQuery = query.toLowerCase();
        return this._skills.filter(skill => 
            skill.text.toLowerCase().includes(lowerQuery)
        );
    }
};

document.addEventListener('DOMContentLoaded', () => {
    if (typeof window.Iconify === 'undefined') {
        console.error('Iconify not loaded! Please ensure the Iconify script is included before this script.');
        return;
    }
    window.skillIconsHelper = new SkillIconsHelper();
    window.skillsHelper.initialize();
});