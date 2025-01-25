import Alpine from 'alpinejs'
import { persist } from '@alpinejs/persist'

// Initialize store as soon as Alpine is ready
document.addEventListener('alpine:init', initializeStore);

// Global Store initialization
export function initializeStore() {
    // Global Store
    const store = {
        theme: {
            // Initialize with persisted value or default
            current: Alpine.$persist('Jobless').as('app_theme_current'),
            themes: ['Jobless', 'Dark', 'lofi', 'pastel'],
            set(theme) {
                this.current = theme;
                document.documentElement.setAttribute('data-theme', theme);
            }
        },

        sidebar: {
            open: Alpine.$persist(window.innerWidth >= 1024).as('app_sidebar_open'),
            collapsed: Alpine.$persist(false).as('app_sidebar_collapsed'),
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
                setTimeout(() => {
                    this.isLoading = false;
                }, 100);

                document.addEventListener("alpine:initialized", () => {
                    this.setupEventListeners();
                });
            },
            setupEventListeners() {
                document.addEventListener("visibilitychange", () => {
                    if (document.visibilityState === "visible") {
                        this.isLoading = false;
                    }
                });
                
                window.addEventListener("beforeunload", () => {
                    this.isLoading = true;
                });
            }
        },

        skills: {
            selected: Alpine.$persist([]).as('app_skills_selected'),
            maxSkills: 10,
            icons: [],
            categories: [],
            loading: false,
            search: '',
            filteredSkills: [],
            modal: {
                open: false,
                ready: false
            },

            init() {
                this.icons = this.initializeSkillIcons();
                this.filteredSkills = [...this.icons];
                this.initializeCategories();
                this.loadInitialSkills();
                this.setupEventListeners();
            },

            initializeSkillIcons() {
                try {
                    if (!window.MODAL_ICON_MAPPING) return [];
                    return Object.entries(window.MODAL_ICON_MAPPING).map(([name, icon]) => ({
                        name: name.charAt(0).toUpperCase() + name.slice(1),
                        icon,
                        icon_dark: window.MODAL_DARK_VARIANTS?.[icon] || icon
                    })).sort((a, b) => a.name.localeCompare(b.name));
                } catch (e) {
                    console.error('Error initializing skill icons:', e);
                    return [];
                }
            },

            initializeCategories() {
                this.categories = [...new Set(this.icons.map(skill => {
                    const category = skill.name.split(' ')[0] || '';
                    return category.charAt(0).toUpperCase() + category.slice(1);
                }))].sort();
            },

            loadInitialSkills() {
                const skillsInput = document.getElementById('id_skills');
                if (skillsInput?.value) {
                    try {
                        const skills = skillsInput.value.split(',')
                            .map(s => s.trim())
                            .filter(Boolean);
                        
                        this.clear();
                        skills.forEach(name => {
                            this.add({
                                name,
                                icon: window.MODAL_ICON_MAPPING?.[name.toLowerCase()] || 'heroicons:academic-cap',
                                icon_dark: window.MODAL_DARK_VARIANTS?.[window.MODAL_ICON_MAPPING?.[name.toLowerCase()]] || 'heroicons:academic-cap'
                            });
                        });
                    } catch (e) {
                        console.error('Error parsing initial skills:', e);
                    }
                }
            },

            setupEventListeners() {
                window.addEventListener('skills-updated', (e) => {
                    if (Array.isArray(e.detail)) {
                        this.selected = e.detail;
                        this.updateHiddenInput();
                    }
                });

                window.addEventListener('skills-restored', () => {
                    this.loadInitialSkills();
                });
            },

            add(skill) {
                if (this.selected.length >= this.maxSkills) return false;
                if (!this.selected.some(s => s.name === skill.name)) {
                    this.selected.push(skill);
                    this.updateHiddenInput();
                    return true;
                }
                return false;
            },

            remove(skillName) {
                this.selected = this.selected.filter(s => s.name !== skillName);
                this.updateHiddenInput();
            },

            clear() {
                this.selected = [];
                this.updateHiddenInput();
            },

            has(skillName) {
                return this.selected.some(s => s.name === skillName);
            },

            getDarkIconForSkill(skillName) {
                const skill = this.selected.find(s => s.name === skillName);
                return skill?.icon_dark || skill?.icon || 'heroicons:academic-cap';
            },

            filterSkills(query = '') {
                const searchTerm = query.toLowerCase();
                this.filteredSkills = !searchTerm ? [...this.icons] : 
                    this.icons.filter(skill => skill.name.toLowerCase().includes(searchTerm));
            },

            updateHiddenInput() {
                const skillsInput = document.getElementById('id_skills');
                if (skillsInput) {
                    skillsInput.value = this.selected.map(s => s.name).join(',');
                    skillsInput.dispatchEvent(new Event('change', { bubbles: true }));
                    
                    // Update display if container exists
                    this.updateSelectedSkillsDisplay();
                }
            },

            updateSelectedSkillsDisplay() {
                const container = document.querySelector('.selected-skills');
                if (!container) return;

                container.innerHTML = '';
                
                if (this.selected.length === 0) {
                    container.innerHTML = '<div class="text-base-content/60 text-sm">Click \'Manage Skills\' to add required skills</div>';
                    return;
                }

                this.selected.forEach(skill => {
                    const badge = document.createElement('div');
                    badge.className = 'badge badge-lg gap-2 group relative overflow-hidden p-4 ' +
                        'bg-primary hover:bg-primary/20 ' +
                        'border border-primary/30 hover:border-primary ' +
                        'text-primary-content/90 hover:text-primary-content ' +
                        'transition-all duration-200 ease-in-out ' +
                        'transform hover:scale-105 hover:shadow-md';

                    badge.innerHTML = `
                        <div class="w-8 h-8 flex items-center justify-center text-primary group-hover:scale-110 transition-transform duration-200">
                            <iconify-icon icon="${skill.icon_dark || skill.icon || 'heroicons:academic-cap'}"></iconify-icon>
                        </div>
                        <span class="font-medium">${skill.name}</span>
                        <button type="button" 
                                class="ml-1 rounded-full p-1.5 hover:bg-primary/20 active:bg-primary/30
                                       transition-all duration-200 opacity-60 hover:opacity-100"
                                title="Remove skill">
                            <iconify-icon icon="heroicons:x-mark" class="text-sm"></iconify-icon>
                        </button>`;

                    badge.querySelector('button').addEventListener('click', () => {
                        this.remove(skill.name);
                    });

                    container.appendChild(badge);
                });
            },

            openModal() {
                this.modal.open = true;
                this.modal.ready = true;
                this.search = '';
                this.filterSkills('');
            },

            closeModal() {
                this.modal.open = false;
                this.search = '';
            }
        }
    };
    
    Alpine.store('app', store);

    // Initialize states after store creation
    Alpine.store('app').pageState.init();
    Alpine.store('app').skills.init();
}

export default {
    initializeStore
};
