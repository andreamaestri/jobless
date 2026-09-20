document.addEventListener("alpine:init", () => {
  Alpine.data("skillSelector", () => ({
    viewMode: "categories",
    searchQuery: "",
    categories: [],
    subcategories: [],
    selectedCategory: null,
    selectedSubcategory: null,
    selectedSkills: [],
    allSkills: [],
    errors: [],
    showMangelberufeOnly: false,
    recentSkills: [],
    recentStorageKey: "jobless_recent_skills",
    proficiencyLevels: [
      { value: 'required', label: gettext('Required'), icon: 'heroicons:exclamation-circle', de: 'Erforderlich' },
      { value: 'preferred', label: gettext('Preferred'), icon: 'heroicons:star', de: 'Bevorzugt' },
      { value: 'bonus', label: gettext('Nice to have'), icon: 'heroicons:plus-circle', de: 'Wünschenswert' }
    ],
    proficiencyLegend: [
      { level: 1, de: 'Grundkenntnisse', en: 'Basic knowledge', desc: 'Elementary understanding or introductory training' },
      { level: 2, de: 'Fortgeschritten', en: 'Intermediate', desc: 'Practical capability under supervision' },
      { level: 3, de: 'Facharbeiter / Geselle', en: 'Skilled worker / Journeyman', desc: 'Completed dual vocational training' },
      { level: 4, de: 'Spezialist / Experte', en: 'Specialist / Expert', desc: 'Certified specialist or senior supervisor' },
      { level: 5, de: 'Meister / Strategisch', en: 'Master / Strategic lead', desc: 'Master craftsman or academic degree holder' }
    ],

    getSkillProficiency(skillId) {
      const skill = this.selectedSkills.find(s => s.id === skillId);
      return skill ? skill.proficiency : null;
    },

    init() {
      const store = Alpine.store("app");
      if (!store?.skills) {
        console.error("Alpine store not initialized properly");
        return;
      }

      this.loadRecentSelections();
      this.loadSkillsData().then(() => {
        if (window.TAGULOUS_INITIAL_TAGS?.length) {
          this.loadInitialSkills(window.TAGULOUS_INITIAL_TAGS);
        }
        this.setupFormValidation();
      });

      Alpine.effect(() => {
        const storeSkills = store.skills.selected;
        if (storeSkills && Array.isArray(storeSkills)) {
          this.syncWithStore(storeSkills);
        }
      });
    },

    syncWithStore(storeSkills) {
      this.selectedSkills = storeSkills.map(skill => ({
        id: skill.id || skill.name,
        label: skill.name,
        label_de: skill.label_de || skill.name,
        icon: skill.icon || window.MODAL_ICON_MAPPING?.[skill.name.toLowerCase()] || "heroicons:academic-cap",
        path: skill.path || "",
        proficiency: skill.proficiency || "required",
        is_mangelberuf: skill.is_mangelberuf || false,
        dqr_level: skill.dqr_level || null,
        certifications: skill.certifications || []
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
          label_de: skill.label_de || skill.label || skill.name,
          icon: skill.icon || window.MODAL_ICON_MAPPING?.[skill.name.toLowerCase()] || "heroicons:academic-cap",
          path: skill.taxonomy_path || skill.path || skill.name || "",
          description: skill.description || "",
          proficiency: "required",
          is_mangelberuf: skill.is_mangelberuf || false,
          dqr_level: skill.dqr_level || null,
          certifications: skill.certifications || []
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
            subcategories: new Map(),
            expanded: false,
            count: 0,
            mangelberufCount: 0
          });
        }

        const cat = categoryMap.get(categoryPath);
        cat.skills.push(skill);
        cat.count += 1;
        if (skill.is_mangelberuf) cat.mangelberufCount += 1;

        // Build subcategory from second path segment
        if (pathParts.length > 2) {
          const subPath = pathParts.slice(0, 2).join("/");
          const subLabel = pathParts[1].replace(/[-_]/g, " ").replace(/\b\w/g, l => l.toUpperCase());
          if (!cat.subcategories.has(subPath)) {
            cat.subcategories.set(subPath, {
              path: subPath,
              label: subLabel,
              skills: [],
              expanded: false,
              count: 0,
              mangelberufCount: 0
            });
          }
          const sub = cat.subcategories.get(subPath);
          sub.skills.push(skill);
          sub.count += 1;
          if (skill.is_mangelberuf) sub.mangelberufCount += 1;
        }
      });

      // Convert Maps to arrays
      this.categories = Array.from(categoryMap.values())
        .map(cat => ({
          ...cat,
          subcategories: Array.from(cat.subcategories.values())
        }))
        .sort((a, b) => a.label.localeCompare(b.label));
    },

    get filteredCategories() {
      if (!this.showMangelberufeOnly) return this.categories;
      return this.categories
        .map(cat => ({
          ...cat,
          skills: cat.skills.filter(s => s.is_mangelberuf),
          subcategories: cat.subcategories
            .map(sub => ({
              ...sub,
              skills: sub.skills.filter(s => s.is_mangelberuf)
            }))
            .filter(sub => sub.skills.length > 0)
        }))
        .filter(cat => cat.skills.length > 0 || cat.subcategories.length > 0);
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
      let skills = this.allSkills;
      
      if (this.showMangelberufeOnly) {
        skills = skills.filter(s => s.is_mangelberuf);
      }

      if (!this.searchQuery) return skills;
      
      const query = this.searchQuery.toLowerCase();
      return skills.filter(
        skill => [skill.label, skill.label_de, skill.description, skill.path]
          .some(value => value.toLowerCase().includes(query))
      );
    },

    get categorySkills() {
      if (!this.selectedCategory) return [];
      let skills = this.selectedCategory.skills;
      if (this.showMangelberufeOnly) {
        skills = skills.filter(s => s.is_mangelberuf);
      }
      return skills;
    },

    get subcategorySkills() {
      if (!this.selectedSubcategory) return [];
      let skills = this.selectedSubcategory.skills;
      if (this.showMangelberufeOnly) {
        skills = skills.filter(s => s.is_mangelberuf);
      }
      return skills;
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

    openCategory(category) {
      this.selectedCategory = category;
      this.selectedSubcategory = null;
      // If category has no subcategories, go directly to skill list
      if (category.subcategories.length === 0) {
        this.viewMode = "category";
      } else {
        this.viewMode = "category";
      }
    },

    openSubcategory(subcategory) {
      this.selectedSubcategory = subcategory;
      this.viewMode = "subcategory";
    },

    backToCategories() {
      this.selectedCategory = null;
      this.selectedSubcategory = null;
      this.viewMode = "categories";
    },

    backToCategory() {
      this.selectedSubcategory = null;
      this.viewMode = "category";
    },

    toggleCategory(category) {
      category.expanded = !category.expanded;
    },

    showSearch() {
      this.viewMode = "search";
      this.searchQuery = "";
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
        this.saveRecentSelection(skill);
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

    // Recent selections persistence
    loadRecentSelections() {
      try {
        const stored = localStorage.getItem(this.recentStorageKey);
        this.recentSkills = stored ? JSON.parse(stored) : [];
      } catch (e) {
        this.recentSkills = [];
      }
    },

    saveRecentSelection(skill) {
      const key = skill.name || skill.label;
      this.recentSkills = [key, ...this.recentSkills.filter(k => k !== key)].slice(0, 5);
      try {
        localStorage.setItem(this.recentStorageKey, JSON.stringify(this.recentSkills));
      } catch (e) {
        // localStorage unavailable
      }
    },

    get recentSkillObjects() {
      return this.recentSkills
        .map(name => this.allSkills.find(s => s.name === name))
        .filter(Boolean)
        .slice(0, 5);
    },

    filterSkills() {
      // filteredSkills getter reacts to searchQuery
    },

    saveSkills() {
      this.updateFormField();
      Alpine.store('app').skills.closeModal();
    },

    skillDisplayName(skill) {
      return skill.label_de && skill.label_de !== skill.label
        ? `${skill.label_de} (${skill.label})`
        : skill.label;
    }
  }));
});
