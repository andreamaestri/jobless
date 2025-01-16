// Motion and animation configuration
const { animate, spring, stagger } = Motion;

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

// Centralized animation sequences
const createAnimations = {
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
};

// Single Alpine initialization
document.addEventListener("alpine:init", () => {
  // Motion helper
  Alpine.magic("motion", () => ({
    animate: (el, keyframes, options = {}) =>
      animate(el, keyframes, options),
  }));

  // Initialize page state if store exists
  if (Alpine.store("pageState")) {
    Alpine.store("pageState").init();
  }
});

// Add passive scroll handler for mobile
document.addEventListener("scroll", () => {}, { passive: true });

// Add passive touch handlers for mobile gestures
document.addEventListener("touchstart", () => {}, { passive: true });
document.addEventListener("touchmove", () => {}, { passive: true });
