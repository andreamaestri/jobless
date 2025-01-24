// Ensure we don't redeclare CONSTANTS
if (typeof CONSTANTS === 'undefined') {
  const CONSTANTS = {
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
}

// Ensure createAnimations isn't redefined
if (typeof createAnimations === 'undefined') {
  const createAnimations = (Motion) => ({
    sidebar: {
      open: {
        transform: ['translateX(-100%)', 'translateX(0%)'],
        opacity: [0, 1],
        scale: [0.98, 1],
        options: {
          duration: CONSTANTS.ANIMATION_CONFIG.DURATION.SIDEBAR,
          ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
        }
      },
      close: {
        transform: ['translateX(0%)', 'translateX(-100%)'],
        opacity: [1, 0],
        scale: [1, 0.98],
        options: {
          duration: CONSTANTS.ANIMATION_CONFIG.DURATION.SIDEBAR,
          ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
        }
      }
    },
    content: {
      expand: {
        transform: ['translateX(0)', 'translateX(20rem)'],
        scale: [0.98, 1],
        options: {
          duration: CONSTANTS.ANIMATION_CONFIG.DURATION.CONTENT,
          ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
        }
      },
      collapse: {
        transform: ['translateX(20rem)', 'translateX(5rem)'],
        scale: [1, 0.98],
        options: {
          duration: CONSTANTS.ANIMATION_CONFIG.DURATION.CONTENT,
          ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
        }
      }
    }
  });
}

// Single Alpine initialization with error handling
document.addEventListener("alpine:init", () => {
  try {
    // Initialize Motion if available
    const animations = typeof Motion !== 'undefined' ? createAnimations(Motion) : null;

    // Motion helper
    Alpine.magic("motion", () => ({
      animate: (el, keyframes, options = {}) => {
        if (typeof Motion !== 'undefined') {
          return Motion.animate(el, keyframes, options);
        }
        console.warn('Motion library not loaded');
        return Promise.resolve();
      },
    }));

    // Initialize page state if store exists
    if (Alpine.store("pageState")) {
      Alpine.store("pageState").init();
    }

  } catch (error) {
    console.error('Error initializing Alpine:', error);
  }
});

// Add passive event listeners for better mobile performance
if (typeof passiveListeners === 'undefined') {
  const passiveListeners = ['scroll', 'touchstart', 'touchmove'];
  passiveListeners.forEach(event => {
    document.addEventListener(event, () => {}, { passive: true });
  });
}

// Modify exports to check for existing values
if (typeof exports !== 'undefined') {
  if (!exports.CONSTANTS) exports.CONSTANTS = CONSTANTS;
  if (!exports.createAnimations) exports.createAnimations = createAnimations;
  if (!exports.passiveListeners) exports.passiveListeners = passiveListeners;
}