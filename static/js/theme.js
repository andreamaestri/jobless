document.addEventListener("alpine:init", () => {
  Alpine.store("theme", {
    themes: ["Jobless", "Dark", "lofi", "pastel"],
    current: localStorage.getItem("theme") || "Jobless",

    init() {
      this.apply();
    },

    apply() {
      document.documentElement.setAttribute("data-theme", this.current);
    },

    set(theme) {
      this.current = theme;
      localStorage.setItem("theme", theme);
      this.apply();
    },
  });

  // Define the pageState store for theme-related loading states
  Alpine.store("pageState", {
    isLoading: true,

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
    },
  });
});
