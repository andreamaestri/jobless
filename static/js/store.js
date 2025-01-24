document.addEventListener('alpine:init', () => {
    // Global Store
    Alpine.store('app', {
        theme: {
            current: 'Jobless',
            themes: ['Jobless', 'Dark', 'lofi', 'pastel'],
            set(theme) {
                this.current = theme;
                document.documentElement.setAttribute('data-theme', theme);
            }
        },
        sidebar: {
            open: false,
            collapsed: false,
            toggle() {
                this.open = !this.open;
            },
            collapse() {
                this.collapsed = !this.collapsed;
            }
        },
        pageState: {
            isLoading: false,
            init() {
                // Initial loading state
                setTimeout(() => {
                    this.isLoading = false;
                }, 100);

                // Initialize after Alpine is ready
                document.addEventListener("alpine:initialized", () => {
                    this.setupEventListeners();
                });
            },
            setupEventListeners() {
                // Handle page visibility changes
                document.addEventListener("visibilitychange", () => {
                    if (document.visibilityState === "visible") {
                        this.isLoading = false;
                    }
                });
                
                // Handle page transitions
                window.addEventListener("beforeunload", () => {
                    this.isLoading = true;
                });
            }
        }
    });

    // Initialize persisted values after defining the store
    Alpine.effect(() => {
        // Access and persist theme
        const persistedTheme = Alpine.$persist(Alpine.store('app').theme).as('app_theme');
        // Update individual properties of the theme object
        Alpine.store('app').theme.current = persistedTheme.current;

        // Access and persist sidebar state
        const persistedSidebar = Alpine.$persist(Alpine.store('app').sidebar).as('app_sidebar');
        // Update individual properties of the sidebar object
        Alpine.store('app').sidebar.open = persistedSidebar.open;
        Alpine.store('app').sidebar.collapsed = persistedSidebar.collapsed;

        // Access and persist page state
        const persistedPageState = Alpine.$persist(Alpine.store('app').pageState).as('app_pageState');
        // Update individual properties of the pageState object
        Alpine.store('app').pageState.isLoading = persistedPageState.isLoading;
    });
});
