document.addEventListener("alpine:init", () => {
  // Wait for SKILL_ICONS to be available
  const waitForSkillIcons = async () => {
    while (!window.skillIconsHelper?.initialized) {
      await new Promise(resolve => setTimeout(resolve, 50));
    }
    return true;
  };

  // Initialize stores first
  if (!Alpine.store('theme')) {
    Alpine.store('theme', {
      themes: ["Jobless", "Dark", "lofi", "pastel"],
      current: localStorage.getItem("theme") || "Jobless"
    });
  }

  if (!Alpine.store('sidebar')) {
    Alpine.store('sidebar', {
      collapsed: JSON.parse(localStorage.getItem("sidebarCollapsed") || "false")
    });
  }

  if (!Alpine.store('pageState')) {
    Alpine.store('pageState', {
      isLoading: false
    });
  }

  Alpine.data('skillsModal', () => ({
    // Core state
    open: false,
    loading: true,
    ready: false,
    isMobile: window.innerWidth < 640,
    isSearchFocused: false,

    // Search state with initialization
    search: '',
    searchQuery: '',
    showSuggestions: false,
    filteredSkills: [],
    browserSearch: '',

    // Category state with initialization
    selectedCategory: null,
    categories: [],
    filteredBrowserSkills: [],
    selectedSkills: [],

    async init() {
      // Wait for SkillIconsHelper to be ready
      await waitForSkillIcons();
      
      // Mobile detection
      this.isMobile = window.innerWidth < 640;
      window.addEventListener('resize', () => {
        this.isMobile = window.innerWidth < 640;
      });

      // Initialize skills state
      await this.initSkills();

      // Watch modal state
      this.$watch('open', value => {
        if (value) {
          this.resetSearchState();
        }
      });

      // Listen for toggle-skill events
      this.$el.addEventListener('toggle-skill', (e) => {
        if (e.detail) {
          this.handleQuickSelect(e.detail);
        }
      });

      this.loading = false;
      this.ready = true;
    },

    async initSkills() {
      try {
        // Initialize from SkillIconsHelper
        this.categories = window.skillIconsHelper?.getCategories() || [];
        this.filteredSkills = [];
        this.filteredBrowserSkills = [];
        
        // Load initial selected skills
        const skillsInput = document.getElementById('id_skills');
        if (skillsInput?.value) {
          const skillNames = skillsInput.value.split(',').map(s => s.trim()).filter(Boolean);
          this.selectedSkills = skillNames.map(name => ({
            name,
            icon: window.skillIconsHelper.getIconForSkill(name),
            icon_dark: window.skillIconsHelper.getIconForSkill(name, true)
          }));
        }
      } catch (error) {
        console.error('Error initializing skills:', error);
      }
    },

    resetSearchState() {
      this.search = '';
      this.searchQuery = '';
      this.showSuggestions = false;
      this.browserSearch = '';
      this.selectedCategory = null;
      this.filteredSkills = [];
      this.filteredBrowserSkills = [];
      this.resetSearch();
    },

    resetSearch() {
      if (this.ready && this.$refs.skillsContainer) {
        this.handleSearch({ target: { value: '' } });
      }
    },

    handleSkillsUpdate(e) {
      if (!this.ready || !e?.detail?.selectedSkills) return;
      
      this.selectedSkills = Array.isArray(e.detail.selectedSkills) ? 
        e.detail.selectedSkills : [];
        
      if (e.isTrusted) {
        this.open = true;
      }
    },

    handleQuickSelect(skill) {
      if (!skill?.name || !this.ready) return;

      const index = this.selectedSkills.findIndex(s => 
        s.name.toLowerCase() === skill.name.toLowerCase()
      );

      if (index === -1) {
        this.selectedSkills.push({
          name: skill.name,
          icon: window.skillIconsHelper.getIconForSkill(skill.name),
          icon_dark: window.skillIconsHelper.getIconForSkill(skill.name, true)
        });
      } else {
        this.selectedSkills.splice(index, 1);
      }

      this.$dispatch('skills-updated', this.selectedSkills);
    },

    // Rest of the methods remain the same...
    handleSearch(e) {
      if (!this.ready || !this.$refs.skillsContainer) {
        this.filteredSkills = [];
        return;
      }

      const query = e.target.value.toLowerCase();
      this.searchQuery = query;
      this.browserSearch = query;
      this.showSuggestions = query.length > 0;

      this.$refs.skillsContainer.querySelectorAll('.skill-group').forEach(group => {
        let hasVisible = false;
        group.querySelectorAll('.skill-card').forEach(card => {
          const name = card.querySelector('.skill-name').textContent.toLowerCase();
          const visible = !query || name.includes(query);
          card.style.display = visible ? '' : 'none';
          if (visible) hasVisible = true;
        });
        group.style.display = hasVisible ? '' : 'none';
      });
    },

    save() {
      if (this.ready) {
        this.$dispatch('skills-updated', this.selectedSkills);
        this.close();
      }
    },

    cancel() {
      window.dispatchEvent(new CustomEvent('skills-restored'));
      this.close();
    },

    close() {
      this.open = false;
      this.resetSearchState();
    }
  }));
});
