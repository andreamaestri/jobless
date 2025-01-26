document.addEventListener("alpine:init", () => {
  Alpine.data("skillSelector", () => ({
    viewMode: "search",
    searchQuery: "",
    categories: [],
    selectedSkills: [],
    allSkills: [],
    errors: [],

    init() {
      const store = Alpine.store("skills");
      this.loadSkillsData(store.tagulousSettings || {});
      
      if (store.initialTags?.length) {
        this.loadInitialSkills(store.initialTags);
      }

      // Set up form validation listener
      this.setupFormValidation();
    },

    loadSkillsData(settings) {
      try {
        const choices = settings.autocomplete_choices || [];
        const store = Alpine.store("skills");

        this.allSkills = choices.map(choice => ({
          id: choice[0],
          label: choice[1],
          icon: store.iconMapping[choice[1]] || "heroicons:academic-cap",
          path: choice[2] || "",
          proficiency: "required"
        }));

        this.buildCategoryTree();
      } catch (error) {
        console.error("Error loading skills data:", error);
        this.errors.push("Failed to load skills data");
      }
    },

    buildCategoryTree() {
      const categoryMap = new Map();

      this.allSkills.forEach(skill => {
        const pathParts = skill.path.split(":");
        
        if (pathParts.length > 1) {
          const categoryPath = pathParts.slice(0, -1).join(":");
          const categoryLabel = pathParts[pathParts.length - 2] || "Uncategorized";

          if (!categoryMap.has(categoryPath)) {
            categoryMap.set(categoryPath, {
              path: categoryPath,
              label: categoryLabel,
              skills: [],
              expanded: false
            });
          }
          categoryMap.get(categoryPath).skills.push(skill);
        }
      });

      this.categories = Array.from(categoryMap.values());
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
        this.errors.push("Failed to load initial skills");
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
        this.errors.push("Please select at least one skill");
        return false;
      }

      const invalidSkills = this.selectedSkills.filter(
        skill => !skill.proficiency || !this.isValidProficiency(skill.proficiency)
      );

      if (invalidSkills.length > 0) {
        this.errors.push("Some skills have invalid proficiency levels");
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
        skill => skill.label.toLowerCase().includes(query)
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

    updateFormField() {
      const input = document.querySelector('input[name="skills"]');
      if (input) {
        input.value = this.skillsJson;
        input.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
  }));
});