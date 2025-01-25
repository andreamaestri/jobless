// Helper functions
export function setupHover(element, callback) {
    const start = () => callback();
    
    element.addEventListener('mouseenter', start);
    element.addEventListener('mouseleave', callback);
    element.addEventListener('touchstart', start, { passive: true });
    element.addEventListener('touchend', callback);
    element.addEventListener('touchcancel', callback);

    return () => {
        element.removeEventListener('mouseenter', start);
        element.removeEventListener('mouseleave', callback);
        element.removeEventListener('touchstart', start);
        element.removeEventListener('touchend', callback);
        element.removeEventListener('touchcancel', callback);
    };
}

// Iconify helper class
export class SkillIconsHelper {
    constructor() {
        this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.watchThemeChanges();
        this.initialized = true;
        this.iconMappings = {};
    }

    async initialize() {
        try {
            // Fetch icon mappings from server if needed
            if (!window.MODAL_ICON_MAPPING) {
                const response = await fetch('/jobs/api/skills/');
                if (!response.ok) throw new Error('Failed to load skills data');
                const skills = await response.json();
                
                // Create mapping from skills data
                skills.forEach(skill => {
                    this.iconMappings[skill.name.toLowerCase()] = skill.icon;
                });
            } else {
                // Use pre-loaded mappings
                this.iconMappings = window.MODAL_ICON_MAPPING;
            }
            
            await this.updateIcons();
            console.log('Icons initialized successfully');
        } catch (error) {
            console.warn('Icon initialization error:', error);
        }
    }

    async refreshIconElement(element, skillName) {
        if (!element || !skillName) return;
        
        try {
            element.style.display = 'inline-block';
            element.style.visibility = 'visible';
            
            // Use Tagulous-provided mapping or fallback
            const iconKey = skillName.toLowerCase();
            const icon = this.iconMappings[iconKey] || window.MODAL_ICON_MAPPING?.[iconKey] || 'heroicons:academic-cap';
            const darkIcon = window.MODAL_DARK_VARIANTS?.[icon] || icon;
            
            element.setAttribute('icon', this.darkMode ? darkIcon : icon);
            element.setAttribute('width', '20');
            element.setAttribute('height', '20');

            // Force icon refresh
            const parent = element.parentElement;
            if (parent) {
                const nextSibling = element.nextSibling;
                element.remove();
                if (nextSibling) {
                    parent.insertBefore(element, nextSibling);
                } else {
                    parent.appendChild(element);
                }
            }
        } catch (error) {
            console.warn(`Failed to refresh icon for skill: ${skillName}`);
            element.setAttribute('icon', 'heroicons:academic-cap');
        }
    }

    watchThemeChanges() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            this.darkMode = e.matches;
            this.updateIcons();
        });
    }

    async updateIcons() {
        // Update all iconify icons in the document
        const icons = document.querySelectorAll('iconify-icon');
        for (const icon of icons) {
            const skillName = icon.closest('[data-tip]')?.getAttribute('data-tip') || 
                            icon.closest('.skill-card')?.querySelector('.skill-name')?.textContent;
            if (skillName) {
                await this.refreshIconElement(icon, skillName);
            }
        }
    }

    getIconForSkill(skillName) {
        const iconKey = skillName.toLowerCase();
        return this.iconMappings[iconKey] || window.MODAL_ICON_MAPPING?.[iconKey] || 'heroicons:academic-cap';
    }

    getDarkIconForSkill(skillName) {
        const icon = this.getIconForSkill(skillName);
        return window.MODAL_DARK_VARIANTS?.[icon] || icon;
    }
}

// Initialize when module is imported
async function initialize() {
    try {
        // Initialize skill icons helper
        if (!window.skillIconsHelper) {
            window.skillIconsHelper = new SkillIconsHelper();
            await window.skillIconsHelper.initialize();
        }
    } catch (error) {
        console.warn('Skills initialization error:', error);
    }
}

// Create instance
window.skillIconsHelper = new SkillIconsHelper();
initialize().catch(console.warn);
