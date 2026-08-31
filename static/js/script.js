// Global constants
export const CONSTANTS = {
    MOBILE_BREAKPOINT: 1024,
    SWIPE_THRESHOLD: 100,
    ANIMATION_CONFIG: {
        DURATION: {
            SIDEBAR: 0.3,
            CONTENT: 0.4,
            STAGGER: 0.03
        },
        OVERSHOOT: {
            DEFAULT: [0.34, 1.56, 0.64, 1]
        },
        EASE: {
            SMOOTH: [0.22, 1, 0.36, 1]
        }
    },
    SIDEBAR: {
        WIDTH: {
            EXPANDED: '20rem',
            COLLAPSED: '5rem'
        }
    }
};

// Animation configurations
export const animations = {
    sidebar: {
        open: {
            keyframes: {
                transform: ['translateX(-100%)', 'translateX(0%)'],
                opacity: [0, 1],
                scale: [0.98, 1]
            },
            options: {
                duration: CONSTANTS.ANIMATION_CONFIG.DURATION.SIDEBAR,
                 ease: CONSTANTS.ANIMATION_CONFIG.OVERSHOOT.DEFAULT
            }
        },
        close: {
            keyframes: {
                transform: ['translateX(0%)', 'translateX(-100%)'],
                opacity: [1, 0],
                scale: [1, 0.98]
            },
            options: {
                duration: CONSTANTS.ANIMATION_CONFIG.DURATION.SIDEBAR,
                 ease: CONSTANTS.ANIMATION_CONFIG.OVERSHOOT.DEFAULT
            }
        }
    },
    content: {
        expand: {
            keyframes: {
                transform: ['translateX(0)', 'translateX(20rem)'],
                scale: [0.98, 1]
            },
            options: {
                duration: CONSTANTS.ANIMATION_CONFIG.DURATION.CONTENT,
                 ease: CONSTANTS.ANIMATION_CONFIG.OVERSHOOT.DEFAULT
            }
        },
        collapse: {
            keyframes: {
                transform: ['translateX(20rem)', 'translateX(5rem)'],
                scale: [1, 0.98]
            },
            options: {
                duration: CONSTANTS.ANIMATION_CONFIG.DURATION.CONTENT,
                 ease: CONSTANTS.ANIMATION_CONFIG.OVERSHOOT.DEFAULT
            }
        }
    }
};

// Add passive event listeners for better mobile performance
const passiveListeners = ['scroll', 'touchstart', 'touchmove'];
passiveListeners.forEach(event => {
    document.addEventListener(event, () => {}, { passive: true });
});

// Initialize page state when this feature module is loaded.
document.addEventListener('alpine:initialized', () => {
    const pageState = Alpine.store('app')?.pageState;
    if (typeof pageState?.init === 'function') pageState.init();
});

// Fill the structured fields from a pasted job advert.
document.addEventListener('DOMContentLoaded', () => {
    const parser = document.getElementById('description-parser');
    const button = document.getElementById('parse-button');
    const paste = document.getElementById('paste');
    const error = document.getElementById('parse-error');
    if (!parser || !button || !paste) return;

    const csrf = parser.querySelector('[name=csrfmiddlewaretoken]')?.value;
    const setValue = (id, value) => {
        const field = document.getElementById(id);
        if (field && value) {
            field.value = value;
            field.dispatchEvent(new Event('input', { bubbles: true }));
            field.dispatchEvent(new Event('change', { bubbles: true }));
        }
    };

    button.addEventListener('click', async () => {
        error.textContent = '';
        error.classList.add('hidden');
        if (!paste.value.trim()) {
            error.textContent = gettext('Please add a job posting first.');
            error.classList.remove('hidden');
            return;
        }

        button.disabled = true;
        button.querySelector('.loading-spinner')?.classList.remove('hidden');
        try {
            const response = await fetch(parser.dataset.url, {
                method: 'POST',
                headers: { 'X-CSRFToken': csrf, 'X-Requested-With': 'XMLHttpRequest' },
                body: new URLSearchParams({ description: paste.value })
            });
            const data = await response.json();
            if (!response.ok) throw new Error(data.error || gettext('The job posting could not be processed.'));

            setValue('id_title', data.title);
            setValue('id_company', data.company);
            setValue('id_location', data.location);
            setValue('id_salary_range', data.salary_range);
            setValue('id_url', data.url);
            setValue('id_description', data.description || paste.value);

            if (Array.isArray(data.skills)) {
                const skills = Alpine.store('app').skills;
                const available = await fetch('/jobs/api/skills/').then(response => response.json());
                const byName = new Map((available.skills || []).map(skill => [
                    (skill.name || skill.label).toLowerCase(), skill
                ]));
                skills.clear();
                data.skills.forEach(name => {
                    const skill = byName.get(String(name).toLowerCase());
                    if (skill) skills.add({
                        id: skill.id,
                        name: skill.name || skill.label,
                        icon: skill.icon || window.MODAL_ICON_MAPPING?.[String(name).toLowerCase()] || 'heroicons:academic-cap'
                    });
                });
                skills.updateHiddenInput();
            }
            button.querySelector('.button-text').textContent = gettext('Filled');
        } catch (err) {
            error.textContent = err.message;
            error.classList.remove('hidden');
        } finally {
            button.disabled = false;
            button.querySelector('.loading-spinner')?.classList.add('hidden');
        }
    });
});
