document.addEventListener("alpine:init", () => {
  Alpine.store("sidebar", {
    open: window.innerWidth >= CONSTANTS.MOBILE_BREAKPOINT,
    collapsed: JSON.parse(localStorage.getItem("sidebarCollapsed") || "false"),

    // Touch handling state
    touchState: {
      startX: 0,
      startY: 0,
      endX: 0,
      endY: 0,
      isSwiping: false
    },

    // Improved touch handling
    handleTouch: {
      start(e) {
        // Ignore touch on scrollable elements
        if (e.target.closest('.scrollable, .slider, input, button, a')) return;
        
        this.touchState = {
          startX: e.touches[0].clientX,
          startY: e.touches[0].clientY,
          endX: e.touches[0].clientX,
          endY: e.touches[0].clientY,
          isSwiping: true
        };
      },

      move(e) {
        if (!this.touchState?.isSwiping) return;
        
        this.touchState.endX = e.touches[0].clientX;
        this.touchState.endY = e.touches[0].clientY;
        
        // Prevent page scroll during swipe
        if (Math.abs(this.touchState.endX - this.touchState.startX) > 10) {
          e.preventDefault();
        }
      },

      end() {
        if (!this.touchState?.isSwiping) return;

        const diffX = this.touchState.startX - this.touchState.endX;
        const diffY = Math.abs(this.touchState.startY - this.touchState.endY);

        // Only handle horizontal swipes with minimal vertical movement
        if (Math.abs(diffX) > CONSTANTS.SWIPE_THRESHOLD && diffY < CONSTANTS.SWIPE_THRESHOLD / 2) {
          const isMobile = window.innerWidth < CONSTANTS.MOBILE_BREAKPOINT;
          if (isMobile) {
            this.open = diffX < 0; // Open on right swipe, close on left swipe
          }
        }

        this.touchState = null;
      }
    },

    // Improved toggle with better animation handling
    async toggle() {
      const elements = {
        sidebar: document.querySelector('aside'),
        content: document.querySelector('main'),
        items: document.querySelectorAll('.nav-item'),
        icons: document.querySelectorAll('.icon-animate')
      };

      // Prevent multiple toggles during animation
      if (this.isAnimating) return;
      this.isAnimating = true;

      try {
        this.open = !this.open;
        const animations = createAnimations;

        if (this.open) {
          // Opening sequence
          await Promise.all([
            animate(elements.sidebar, animations.sidebar.open),
            animate(elements.content, animations.content.expand)
          ]);

          // Animate nav items with stagger
          animate(elements.items, {
            opacity: [0, 1],
            transform: ['translateX(-20px) scale(0.9)', 'translateX(0) scale(1)']
          }, {
            delay: stagger(CONSTANTS.ANIMATION_CONFIG.DURATION.STAGGER),
            duration: CONSTANTS.ANIMATION_CONFIG.DURATION.SIDEBAR,
            ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
          });
        } else {
          // Closing sequence
          await animate(elements.items, {
            opacity: [1, 0],
            transform: ['translateX(0) scale(1)', 'translateX(-20px) scale(0.9)']
          }, {
            duration: CONSTANTS.ANIMATION_CONFIG.DURATION.SIDEBAR * 0.5,
            ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
          }).finished;

          await Promise.all([
            animate(elements.sidebar, animations.sidebar.close),
            animate(elements.content, animations.content.collapse)
          ]);
        }
      } finally {
        this.isAnimating = false;
      }
    },

    // Improved collapse with better performance
    async collapse() {
      if (this.isAnimating) return;
      this.isAnimating = true;

      try {
        this.collapsed = !this.collapsed;
        localStorage.setItem('sidebarCollapsed', this.collapsed);

        const elements = {
          sidebar: document.querySelector('aside'),
          icons: document.querySelectorAll('.icon-animate')
        };

        // Optimize performance with will-change
        elements.sidebar.style.willChange = 'transform, width';

        // Animate sidebar width
        await animate(elements.sidebar, {
          width: this.collapsed ? 
            CONSTANTS.SIDEBAR.WIDTH.COLLAPSED : 
            CONSTANTS.SIDEBAR.WIDTH.EXPANDED
        }, {
          duration: CONSTANTS.ANIMATION_CONFIG.DURATION.SIDEBAR,
          ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
        }).finished;

        // Animate icons
        await animate(elements.icons, {
          scale: this.collapsed ? [1, 1.2] : [1.2, 1]
        }, {
          duration: CONSTANTS.ANIMATION_CONFIG.DURATION.SIDEBAR,
          ease: CONSTANTS.ANIMATION_CONFIG.SPRING.DEFAULT
        }).finished;

        // Cleanup
        elements.sidebar.style.willChange = 'auto';
      } finally {
        this.isAnimating = false;
      }
    },

    // Improved initialization with better event handling
    init() {
      // Debounced resize handler
      const handleResize = () => {
        const isMobile = window.innerWidth < CONSTANTS.MOBILE_BREAKPOINT;
        if (isMobile) {
          this.open = false;
          this.collapsed = false;
          document.body.style.overflow = this.open ? 'hidden' : '';
        } else {
          this.open = true;
          document.body.style.overflow = '';
        }
      };

      // Throttled resize listener
      let resizeTimeout;
      window.addEventListener('resize', () => {
        if (!resizeTimeout) {
          resizeTimeout = setTimeout(() => {
            handleResize();
            resizeTimeout = null;
          }, 100);
        }
      }, { passive: true });

      // Touch event handlers
      document.addEventListener('touchstart', (e) => this.handleTouch.start.call(this, e), { passive: false });
      document.addEventListener('touchmove', (e) => this.handleTouch.move.call(this, e), { passive: false });
      document.addEventListener('touchend', () => this.handleTouch.end.call(this), { passive: true });

      // Click outside handler for mobile
      document.addEventListener('click', (e) => {
        if (window.innerWidth < CONSTANTS.MOBILE_BREAKPOINT && 
            this.open && 
            !e.target.closest('aside')) {
          this.open = false;
        }
      }, { passive: true });

      // Escape key handler
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && 
            this.open && 
            window.innerWidth < CONSTANTS.MOBILE_BREAKPOINT) {
          this.open = false;
        }
      });

      // Initialize state
      this.isAnimating = false;
      this.touchState = null;
      handleResize();
      
      // Set initial collapsed state
      this.collapsed = window.innerWidth >= CONSTANTS.MOBILE_BREAKPOINT ? 
        JSON.parse(localStorage.getItem('sidebarCollapsed') || 'false') : 
        false;
    },
  });
});
