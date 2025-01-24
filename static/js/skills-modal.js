document.addEventListener("alpine:init", () => {
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

    // Search and filtering state
    search: '',
    searchQuery: '',
    showSuggestions: false,
    filteredSkills: [],
    browserSearch: '',
    
    // Category management
    selectedCategory: null,
    categories: [],
    filteredBrowserSkills: [],
    selectedSkills: [],

    init() {
      // Mobile detection
      this.isMobile = window.innerWidth < 640;
      window.addEventListener('resize', () => {
        this.isMobile = window.innerWidth < 640;
      });

      // Initialize variables
      this.initializeState();

      // Watch modal state
      this.$watch('open', value => {
        if (value) {
          this.search = '';
          this.searchQuery = '';
          this.showSuggestions = false;
          this.filteredSkills = [];
          this.browserSearch = '';
          this.selectedCategory = null;
          this.resetSearch();
        }
      });

      // Listen for toggle-skill events
      this.$el.addEventListener('toggle-skill', (e) => {
        if (e.detail) {
          this.handleQuickSelect(null, e.detail);
        }
      });
    },

    initializeState() {
      // Wait for icon mappings to be available
      this.waitForDependencies().then(() => {
        this.categories = this.getUniqueCategories();
        this.filteredSkills = [];
        this.filteredBrowserSkills = [];
        this.loading = false;
        this.ready = true;
      });
    },

    async waitForDependencies() {
      while (!window.MODAL_ICON_MAPPING || !window.MODAL_DARK_VARIANTS) {
        await new Promise(resolve => setTimeout(resolve, 50));
      }
      return true;
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

    isSelected(skillName) {
      return this.selectedSkills.some(skill => 
        skill.name.toLowerCase() === skillName.toLowerCase()
      );
    },

    getDarkIconForSkill(skillName) {
      const icon = window.MODAL_ICON_MAPPING?.[skillName.toLowerCase()];
      if (icon) {
        return window.MODAL_DARK_VARIANTS?.[icon] || icon;
      }
      return 'heroicons:academic-cap';
    },

    handleQuickSelect(event, skill) {
      if (!skill?.name) return;

      const index = this.selectedSkills.findIndex(s => 
        s.name.toLowerCase() === skill.name.toLowerCase()
      );

      if (index === -1) {
        this.selectedSkills.push({
          name: skill.name,
          icon: window.MODAL_ICON_MAPPING?.[skill.name.toLowerCase()] || 'heroicons:academic-cap',
          icon_dark: this.getDarkIconForSkill(skill.name)
        });
      } else {
        this.selectedSkills.splice(index, 1);
      }

      this.$dispatch('skills-updated', this.selectedSkills);
    },

    handleSearch(e) {
      if (!this.ready || !this.$refs.skillsContainer) {
        this.filteredSkills = [];
        return;
      }
      
      const query = e.target.value.toLowerCase();
      this.searchQuery = query;
      this.browserSearch = query;
      this.showSuggestions = query.length > 0;
      
      // Reset filtered skills
      this.filteredSkills = [];

      this.$refs.skillsContainer.querySelectorAll('.skill-group').forEach(group => {
        let hasVisible = false;
        group.querySelectorAll('.skill-card').forEach(card => {
          const name = card.querySelector('.skill-name').textContent.toLowerCase();
          const visible = !query || name.includes(query);
          card.style.display = visible ? '' : 'none';
          if (visible) hasVisible = true;
        });
        group.style.display = hasVisible ? '' : 'none';
        
        // Add visible skills to filtered list
        if (hasVisible) {
          const visibleCards = Array.from(group.querySelectorAll('.skill-card'))
            .filter(card => card.style.display !== 'none')
            .map(card => JSON.parse(card.dataset.skill));
          this.filteredSkills.push(...visibleCards);
        }
      });

      // Update browser-filtered skills
      this.filteredBrowserSkills = [...this.filteredSkills];
    },
    
    getUniqueCategories() {  
      if (!this.$refs.skillsContainer) return [];
      
      const cards = this.$refs.skillsContainer.querySelectorAll('.skill-card');
      const categories = new Set();
      
      cards.forEach(card => {
        const skill = JSON.parse(card.dataset.skill);
        if (skill.category) categories.add(skill.category);
      });
      
      return Array.from(categories);
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
      this.search = '';
      this.isSearchFocused = false;
      this.resetSearch();
    },

    getVisibleSkillCount() {
      if (!this.ready || !this.$refs.skillsContainer) return 0;
      
      return this.$refs.skillsContainer?.querySelectorAll(
        '.skill-card[style*="display: block"], .skill-card:not([style*="display"])'
      )?.length || 0;
    }
  }));
});
