document.addEventListener('DOMContentLoaded', async () => {
    // Initialize skill icons helper
    window.skillIconsHelper = new SkillIconsHelper();
    await window.skillIconsHelper.initialize();

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
});
