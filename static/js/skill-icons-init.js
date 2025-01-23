document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Initialize skill icons helper
        if (!window.skillIconsHelper) {
            window.skillIconsHelper = new SkillIconsHelper();
            await window.skillIconsHelper.initialize();
        }

        // Update all skill icons in the document
        const updateIcons = () => {
            document.querySelectorAll('iconify-icon').forEach(async (icon) => {
                const skillName = icon.closest('[data-tip]')?.getAttribute('data-tip');
                if (skillName) {
                    await window.skillIconsHelper.refreshIconElement(icon, skillName);
                }
            });
        };

        // Update icons initially
        updateIcons();

        // Watch for theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
            updateIcons();
        });

        // Initialize skills manager only if modal exists
        const skillsModal = document.getElementById('skills-modal');
        if (skillsModal && !window.skillsManager) {
            window.skillsManager = new SkillsModalManager();
        }

        // Initialize skills helper without API dependency
        if (!window.skillsHelper) {
            window.skillsHelper = {
                _skills: [],
                _initialized: true,
                initialize: async function() {
                    // Skip API call, just mark as initialized
                    this._initialized = true;
                },
                updateIcons: function() {
                    // Use existing icon update function
                    updateIcons();
                }
            };
        }

    } catch (error) {
        console.warn('Skills initialization error:', error);
        // Continue gracefully even if initialization fails
    }
});
