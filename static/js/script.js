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
        SPRING: {
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
                ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
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
                ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
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
                ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
            }
        },
        collapse: {
            keyframes: {
                transform: ['translateX(20rem)', 'translateX(5rem)'],
                scale: [1, 0.98]
            },
            options: {
                duration: CONSTANTS.ANIMATION_CONFIG.DURATION.CONTENT,
                ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
            }
        }
    }
};

// Add passive event listeners for better mobile performance
const passiveListeners = ['scroll', 'touchstart', 'touchmove'];
passiveListeners.forEach(event => {
    document.addEventListener(event, () => {}, { passive: true });
});

// Alpine.js initialization with Motion integration
document.addEventListener("alpine:init", () => {
    try {
        // Motion helper
        Alpine.magic("motion", () => ({
            animate: (el, keyframes, options = {}) => {
                if (!window.Motion?.animate) {
                    console.warn('Motion library not loaded');
                    return Promise.resolve();
                }
                return window.Motion.animate(el, keyframes, options);
            },
            applyAnimation: (el, animationName, variant) => {
                if (!window.Motion?.animate) {
                    console.warn('Motion library not loaded');
                    return Promise.resolve();
                }
                
                const animation = animations[animationName]?.[variant];
                if (!animation) {
                    console.warn(`Animation ${animationName}.${variant} not found`);
                    return Promise.resolve();
                }
                
                const { keyframes, options } = animation;
                return window.Motion.animate(el, keyframes, { 
                    duration: options.duration, 
                    ease: options.ease 
                });
            }
        }));

        // Initialize page state if store exists and has init method
        const pageState = Alpine.store("app")?.pageState;
        if (typeof pageState?.init === 'function') {
            pageState.init();
        } else {
            console.warn('pageState store or init method not found');
        }

    } catch (error) {
        console.error('Error initializing Alpine:', error);
        console.debug('Store state:', {
            app: Alpine.store("app"),
            pageState: Alpine.store("app")?.pageState,
            hasInit: typeof Alpine.store("app")?.pageState?.init === 'function'
        });
    }
});