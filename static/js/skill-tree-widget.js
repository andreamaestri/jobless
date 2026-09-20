document.addEventListener("alpine:init", () => {
  Alpine.data("skillSelector", () => ({
    viewMode: "search",
    searchQuery: "",
    categories: [],
    selectedSkills: [],
    allSkills: [],
    errors: [],
    proficiencyLevels: [
      { value: 'required', label: gettext('Required'), icon: 'heroicons:exclamation-circle' },
      { value: 'preferred', label: gettext('Preferred'), icon: 'heroicons:star' },
      { value: 'bonus', label: gettext('Nice to have'), icon: 'heroicons:plus-circle' }
    ],

    getSkillProficiency(skillId) {
      const skill = this.selectedSkills.find(s => s.id === skillId);
      return skill ? skill.proficiency : null;
    },

    init() {
      // Initialize store data first
      const store = Alpine.store("app");
      if (!store?.skills) {
        console.error("Alpine store not initialized properly");
        return;
      }

      // Load initial data
      this.loadSkillsData().then(() => {
        if (window.TAGULOUS_INITIAL_TAGS?.length) {
          this.loadInitialSkills(window.TAGULOUS_INITIAL_TAGS);
        }
        this.setupFormValidation();
      });

      // Watch for store changes
      Alpine.effect(() => {
        const storeSkills = store.skills.selected;
        if (storeSkills && Array.isArray(storeSkills)) {
          this.syncWithStore(storeSkills);
        }
      });
    },

    syncWithStore(storeSkills) {
      // Update local skills based on store
      this.selectedSkills = storeSkills.map(skill => ({
        id: skill.id || skill.name,
        label: skill.name,
        icon: skill.icon || window.MODAL_ICON_MAPPING?.[skill.name.toLowerCase()] || "heroicons:academic-cap",
        path: skill.path || "",
        proficiency: skill.proficiency || "required"
      }));
      this.updateFormField();
    },

    async loadSkillsData() {
      try {
        const response = await fetch('/jobs/api/skills/');
        if (!response.ok) throw new Error(`Skills request failed: ${response.status}`);
        const data = await response.json();
        const skills = (data.skills || []).map(skill => ({
          id: skill.id,
          label: skill.label || skill.name,
          icon: skill.icon || window.MODAL_ICON_MAPPING?.[skill.name.toLowerCase()] || "heroicons:academic-cap",
          path: skill.taxonomy_path || skill.path || skill.name || "",
          description: skill.description || "",
          proficiency: "required"
        }));

        const paths = skills.map(skill => skill.path);
        this.allSkills = skills.filter(skill =>
          !paths.some(path => path !== skill.path && path.startsWith(`${skill.path}/`))
        );
        this.buildCategoryTree();
      } catch (error) {
        console.error("Error loading skills data:", error);
        this.errors.push(gettext("Failed to load skills"));
      }
    },

    buildCategoryTree() {
      const categoryMap = new Map();

      this.allSkills.forEach(skill => {
        const pathParts = skill.path.split("/").filter(Boolean);
        const categoryPath = pathParts.length > 1 ? pathParts[0] : "other";
        const categoryLabel = (pathParts.length > 1 ? pathParts[0] : gettext("Other"))
          .replace(/[-_]/g, " ")
          .replace(/\b\w/g, letter => letter.toUpperCase());
        if (!categoryMap.has(categoryPath)) {
          categoryMap.set(categoryPath, {
            path: categoryPath,
            label: categoryLabel,
            skills: [],
            expanded: false,
            count: 0
          });
        }
        categoryMap.get(categoryPath).skills.push(skill);
        categoryMap.get(categoryPath).count += 1;
      });

      this.categories = Array.from(categoryMap.values())
        .sort((a, b) => a.label.localeCompare(b.label));
    },

    loadInitialSkills(initialTags) {
      try {
        initialTags.forEach(tag => {
          const skill = this.allSkills.find(s => s.id === tag[0]);
          if (skill) {
            this.selectedSkills.push({
              ...skill,
              proficiency: tag[1] || "required"
            });
          }
        });
      } catch (error) {
        console.error("Error loading initial skills:", error);
        this.errors.push(gettext("Failed to load initial skills"));
      }
    },

    setupFormValidation() {
      const form = document.querySelector('form');
      if (!form) return;

      form.addEventListener('submit', (e) => {
        if (!this.validateSkills()) {
          e.preventDefault();
        }
      });
    },

    validateSkills() {
      this.errors = [];
      
      if (this.selectedSkills.length === 0) {
        this.errors.push(gettext("Select at least one skill"));
        return false;
      }

      const invalidSkills = this.selectedSkills.filter(
        skill => !skill.proficiency || !this.isValidProficiency(skill.proficiency)
      );

      if (invalidSkills.length > 0) {
        this.errors.push(gettext("Some skills have invalid proficiency levels"));
        return false;
      }

      return true;
    },

    isValidProficiency(proficiency) {
      return ['required', 'preferred', 'bonus'].includes(proficiency);
    },

    get filteredSkills() {
      if (!this.searchQuery) return this.allSkills;
      
      const query = this.searchQuery.toLowerCase();
      return this.allSkills.filter(
        skill => [skill.label, skill.description, skill.path]
          .some(value => value.toLowerCase().includes(query))
      );
    },

    get skillsJson() {
      return JSON.stringify(
        this.selectedSkills.map(skill => ({
          skill: skill.id,
          proficiency: skill.proficiency,
          name: skill.label
        }))
      );
    },

    toggleCategory(category) {
      category.expanded = !category.expanded;
    },

    isSelected(skillId) {
      return this.selectedSkills.some(skill => skill.id === skillId);
    },

    toggleSkill(skill) {
      if (this.isSelected(skill.id)) {
        this.removeSkill(skill);
      } else {
        this.addSkill(skill);
      }

      this.updateFormField();
      this.dispatchSkillUpdate();
    },

    addSkill(skill) {
      if (!this.isSelected(skill.id)) {
        this.selectedSkills.push({
          ...skill,
          proficiency: "required"
        });
      }
    },

    removeSkill(skill) {
      this.selectedSkills = this.selectedSkills.filter(
        s => s.id !== skill.id
      );
    },

    updateSkill(skill) {
      const index = this.selectedSkills.findIndex(s => s.id === skill.id);
      if (index !== -1) {
        this.selectedSkills[index] = { ...skill };
        this.updateFormField();
      }
    },

    dispatchSkillUpdate() {
      this.$dispatch('skills-updated', {
        detail: this.selectedSkills
      });
    },

    updateFormField() {
      const input = document.querySelector('input[name="skills"]');
      if (input) {
        input.value = this.skillsJson;
        input.dispatchEvent(new Event('change', { bubbles: true }));
        window.dispatchEvent(new CustomEvent('skills-updated', {
          detail: this.selectedSkills
        }));
      }
    },

    filterSkills() {
      // The filteredSkills getter reacts to searchQuery; this method keeps the
      // template event handler explicit and compatible with Alpine.
    },

    saveSkills() {
      this.updateFormField();
      Alpine.store('app').skills.closeModal();
    }
  }));
});
