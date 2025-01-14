function isIconifyReady() {
    return typeof iconifyIcon !== 'undefined' && document.createElement('iconify-icon').constructor !== HTMLElement;
}

class SkillIconsHelper {
    constructor() {
        this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.watchThemeChanges();
        this.initialized = true;
        this.initializationAttempts = 0;
    }

    async initialize() {
        try {
            // Skip waiting and just try to update icons
            await this.updateIcons();
            console.log('Icons initialized successfully');
        } catch (error) {
            console.warn('Falling back to basic functionality:', error);
        }
    }

    async refreshIconElement(element, iconName, darkIconName = null) {
        if (!element || !iconName) return;
        
        try {
            element.style.display = 'inline-block';
            element.style.visibility = 'visible';
            
            const isDark = this.darkMode && darkIconName;
            const icon = isDark ? darkIconName : iconName;
            
            element.setAttribute('icon', icon);
            
            if (darkIconName) {
                element.setAttribute('data-icon', iconName);
                element.setAttribute('data-icon-dark', darkIconName);
            }

            // Force a refresh
            const parent = element.parentElement;
            if (parent) {
                const nextSibling = element.nextSibling;
                element.remove();
                if (nextSibling) {
                    parent.insertBefore(element, nextSibling);
                } else {
                    parent.appendChild(element);
                }
            }
        } catch (error) {
            console.warn(`Failed to refresh icon: ${iconName}`);
            element.setAttribute('icon', 'octicon:code-16');
        }
    }

    watchThemeChanges() {
        const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
        mediaQuery.addEventListener('change', (e) => {
            this.darkMode = e.matches;
            this.updateIcons();
        });
    }

    async updateIcons() {
        const icons = document.querySelectorAll('iconify-icon[data-icon][data-icon-dark]');
        for (const icon of icons) {
            const lightIcon = icon.getAttribute('data-icon');
            const darkIcon = icon.getAttribute('data-icon-dark');
            await this.refreshIconElement(icon, lightIcon, darkIcon);
        }
    }
}

// ... rest of the existing code ...

// Initialize skills helper when page loads
window.skillsHelper = {
    _skills: [],
    _initialized: false,

    async initialize() {
        if (this._initialized) {
            // Always refresh icons if we've already initialized before
            this.updateIcons();
            return;
        }
        try {
            const response = await fetch('/jobs/api/skills/');
            if (!response.ok) throw new Error('Failed to load skills data');
            this._skills = await response.json();
            this._initialized = true;
            this.updateIcons();
        } catch (error) {
            console.error('Failed to initialize skills:', error);
        }
    },

    updateIcons() {
        // Update all skill icons in the document
        document.querySelectorAll('[data-skill-icon]').forEach(element => {
            const iconData = JSON.parse(element.getAttribute('data-skill-icon'));
            const iconify = element.querySelector('.iconify');
            if (iconify) {
                const icon = this.getIconByName(iconData.name);
                iconify.setAttribute('data-icon', icon);
            }
        });
    },

    getIconByName(skillName) {
        const skill = this._skills.find(s => s.text === skillName);
        if (!skill) return 'octicon:code-16';
        return skill.icon;
    },

    getCategories() {
        return [...new Set(this._skills.map(skill => skill.icon.split(':')[0]))];
    },

    filterByCategory(category) {
        return category 
            ? this._skills.filter(skill => skill.icon.startsWith(category + ':'))
            : this._skills;
    },

    searchSkills(query) {
        if (!query) return this._skills;
        const lowerQuery = query.toLowerCase();
        return this._skills.filter(skill => 
            skill.text.toLowerCase().includes(lowerQuery)
        );
    }
};

class SkillSelectManager {
    constructor() {
        this.skillGroups = {
            frontend: {
                name: 'Frontend Development',
                skills: ['JavaScript', 'TypeScript', 'React', 'Vue', 'Angular', 'HTML', 'CSS']
            },
            backend: {
                name: 'Backend Development',
                skills: ['Python', 'Java', 'Node.js', 'PHP', 'Ruby']
            },
            database: {
                name: 'Databases',
                skills: ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis']
            },
            devops: {
                name: 'DevOps & Tools',
                skills: ['Docker', 'Kubernetes', 'AWS', 'Git']
            }
        };

        this.skillKeywords = {
            'JavaScript': ['js', 'javascript', 'es6'],
            'TypeScript': ['ts', 'typescript'],
            'Python': ['py', 'python'],
            'React': ['reactjs', 'react.js'],
            // Add more mappings as needed
        };

        this.skillPriorities = {
            'JavaScript': 100,
            'Python': 95,
            'React': 90,
            'TypeScript': 85,
            // Add more priorities as needed
        };
    }

    initializeSelect(elementId) {
        const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Create backdrop element
        const backdrop = document.createElement('div');
        backdrop.className = 'ts-dropdown-backdrop';
        document.body.appendChild(backdrop);
        
        const select = new TomSelect(elementId, {
            plugins: {
                'remove_button': { title: 'Remove skill' },
                'clear_button': { title: 'Clear all skills' },
                'dropdown_input': {},
                'dropdown_header': {
                    title: 'Search or select skills'
                }
            },
            maxItems: null,
            maxOptions: null,
            valueField: 'name',
            labelField: 'name',
            searchField: ['name', 'keywords'],
            create: false,
            closeAfterSelect: false,
            hideSelected: true,
            persist: false,
            openOnFocus: true,
            preload: true,
            dropdownParent: 'body',
            optgroups: Object.entries(this.skillGroups).map(([id, group]) => ({
                id,
                name: group.name
            })),
            optgroupField: 'group',
            optgroupOrder: ['frontend', 'backend', 'database', 'devops', 'other'],
            score: this.createScoreFunction(),
            render: {
                dropdown: () => {
                    return `
                        <div class="ts-dropdown">
                            <div class="ts-dropdown-header">
                                <input type="text" autocomplete="off" placeholder="Search skills...">
                                <button class="ts-dropdown-close">
                                    <iconify-icon icon="heroicons:x-mark-20-solid" width="20"></iconify-icon>
                                </button>
                            </div>
                            <div class="ts-dropdown-content"></div>
                        </div>
                    `;
                },
                optgroup_header: (data, escape) => 
                    `<div class="optgroup-header">${escape(data.name)}</div>`,
                
                option: (item, escape) => {
                    const icon = isDarkMode ? (item.icon_dark || item.icon) : item.icon;
                    return `<div class="flex items-center gap-3 p-2">
                        <iconify-icon class="text-xl" icon="${escape(icon || 'octicon:code-16')}"></iconify-icon>
                        <div>
                            <div class="font-medium">${escape(item.name)}</div>
                            ${item.description ? `<div class="text-xs text-base-content/70">${escape(item.description)}</div>` : ''}
                        </div>
                    </div>`;
                },

                item: (item, escape) => {
                    const icon = isDarkMode ? (item.icon_dark || item.icon) : item.icon;
                    return `<div class="flex items-center gap-2">
                        <iconify-icon class="text-lg" icon="${escape(icon || 'octicon:code-16')}"></iconify-icon>
                        <span class="font-medium">${escape(item.name)}</span>
                    </div>`;
                },

                no_results: () => 
                    '<div class="no-results">No matching skills found</div>'
            },
            
            onInitialize: function() {
                this.input.style.display = 'none';
                this.control.setAttribute('data-placeholder', 'Click to add skills...');
                
                // Add click handlers for backdrop and close button
                backdrop.addEventListener('click', () => this.close());
                this.dropdown.querySelector('.ts-dropdown-close')
                    ?.addEventListener('click', () => this.close());
                
                // Move search input handling
                const searchInput = this.dropdown.querySelector('input');
                if (searchInput) {
                    searchInput.addEventListener('input', (e) => {
                        this.setTextboxValue(e.target.value);
                        this.refreshOptions(false);
                    });
                }
            },
            
            onDropdownOpen: function() {
                backdrop.classList.add('active');
                document.body.style.overflow = 'hidden';
                
                // Focus search input
                setTimeout(() => {
                    this.dropdown.querySelector('input')?.focus();
                }, 50);
            },
            
            onDropdownClose: function() {
                backdrop.classList.remove('active');
                document.body.style.overflow = '';
                
                // Clear search
                const searchInput = this.dropdown.querySelector('input');
                if (searchInput) searchInput.value = '';
                this.setTextboxValue('');
            },
            
            onType: function(str) {
                // Update search input value
                const searchInput = this.dropdown.querySelector('input');
                if (searchInput) searchInput.value = str;
            }
        });

        // Update dropdown position on scroll
        const container = select.control.closest('.form-section');
        if (container) {
            container.addEventListener('scroll', () => select.close());
        }

        return select;
    }

    createScoreFunction() {
        return function(search) {
            const scoringFunction = this.getScoreFunction(search);
            return (item) => {
                if (!search) return 1;
                if (item.keywords && item.keywords.some(k => 
                    k.toLowerCase().startsWith(search.toLowerCase()))) {
                    return 1;
                }
                return scoringFunction(item);
            };
        };
    }

    getSkillOptions() {
        return Array.from(document.querySelectorAll('#skills-select option')).map(option => {
            const skillData = JSON.parse(option.dataset.skill || '{}');
            return {
                name: skillData.name,
                icon: skillData.icon,
                icon_dark: skillData.icon_dark,
                keywords: this.getSkillKeywords(skillData.name),
                group: this.getSkillGroup(skillData.name),
                priority: this.getSkillPriority(skillData.name)
            };
        });
    }

    getSkillKeywords(name) {
        return this.skillKeywords[name] || [name.toLowerCase()];
    }

    getSkillGroup(name) {
        for (const [group, data] of Object.entries(this.skillGroups)) {
            if (data.skills.includes(name)) return group;
        }
        return 'other';
    }

    getSkillPriority(name) {
        return this.skillPriorities[name] || 50;
    }

    handleThemeChange(select, isDark) {
        const items = select.items;
        select.clear();
        select.clearOptions();
        
        // Update options with dark/light icons based on theme
        select.options = select.options.map(option => ({
            ...option,
            icon: isDark ? (option.icon_dark || option.icon) : option.icon
        }));
        
        select.sync();
        items.forEach(value => select.addItem(value));
    }
}

class SkillsModalManager {
    constructor() {
        this.selectedSkills = new Set();
        this.skillsContainer = document.getElementById('selected-skills');
        this.skillsInput = document.getElementById('skills-input');
        this.skillSearch = document.getElementById('skill-search');
        this.modal = document.getElementById('skills-modal');
        this.iconHelper = window.skillIconsHelper;
        
        this.initializeModal();
    }

    initializeModal() {
        // Load previously selected skills
        if (this.skillsInput.value) {
            this.selectedSkills = new Set(JSON.parse(this.skillsInput.value));
            this.renderSelectedSkills();
        }

        // Setup search functionality
        if (this.skillSearch) {
            this.skillSearch.addEventListener('input', (e) => this.handleSearch(e));
        }

        // Setup modal events
        if (this.modal) {
            this.modal.addEventListener('show', async () => this.handleModalShow());
        }

        // Setup intersection observer for letter navigation
        this.setupLetterObserver();
    }

    handleSearch(e) {
        const query = e.target.value.toLowerCase();
        document.querySelectorAll('#skills-modal label').forEach(label => {
            const skillName = label.querySelector('span').textContent.toLowerCase();
            label.style.display = skillName.includes(query) ? '' : 'none';
        });
    }

    async handleModalShow() {
        // Sync checkboxes with selected skills
        document.querySelectorAll('#skills-modal input[type="checkbox"]').forEach(cb => {
            cb.checked = this.selectedSkills.has(cb.value);
        });
        
        // Clear search
        if (this.skillSearch) {
            this.skillSearch.value = '';
            this.skillSearch.dispatchEvent(new Event('input'));
        }
        
        // Refresh icons
        await this.iconHelper.updateIcons();
    }

    applySelectedSkills() {
        const checkboxes = document.querySelectorAll('#skills-modal input[type="checkbox"]');
        this.selectedSkills.clear();
        checkboxes.forEach(cb => {
            if (cb.checked) {
                this.selectedSkills.add(cb.value);
            }
        });
        this.renderSelectedSkills();
    }

    removeSkill(skillName) {
        this.selectedSkills.delete(skillName);
        this.renderSelectedSkills();
        
        // Also uncheck the checkbox if modal is open
        const checkbox = document.querySelector(`input[value="${skillName}"]`);
        if (checkbox) {
            checkbox.checked = false;
        }
    }

    renderSelectedSkills() {
        if (!this.skillsContainer) return;
        
        this.skillsContainer.innerHTML = '';
        this.skillsInput.value = JSON.stringify([...this.selectedSkills]);
        const isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;

        this.selectedSkills.forEach(skillName => {
            const checkbox = document.querySelector(`input[value="${skillName}"]`);
            if (!checkbox) return;

            const skillData = JSON.parse(checkbox.dataset.skill);
            const icon = isDarkMode && skillData.icon_dark ? skillData.icon_dark : skillData.icon;
            
            const tag = document.createElement('div');
            tag.className = 'flex items-center gap-2 bg-base-200 px-3 py-1.5 rounded-full';
            tag.innerHTML = `
                <iconify-icon icon="${icon}" 
                             data-icon="${skillData.icon}"
                             data-icon-dark="${skillData.icon_dark || skillData.icon}"
                             class="text-xl"
                             width="20"></iconify-icon>
                <span>${skillData.name}</span>
                <button type="button" class="btn btn-xs btn-ghost btn-circle">
                    <iconify-icon icon="heroicons:x-mark-20-solid"></iconify-icon>
                </button>
            `;

            // Add click handler
            const removeBtn = tag.querySelector('button');
            removeBtn.addEventListener('click', () => this.removeSkill(skillName));
            
            this.skillsContainer.appendChild(tag);
        });
    }

    jumpToLetter(letter) {
        const group = document.querySelector(`.skill-group[data-letter="${letter}"]`);
        if (!group) return;

        const container = document.querySelector('.modal-box .overflow-y-auto');
        const header = document.querySelector('.modal-box .flex-none');
        const offset = header ? header.offsetHeight : 0;

        container.scrollTo({
            top: group.offsetTop - offset - 8,
            behavior: 'smooth'
        });

        // Show visual feedback
        showLetterPreview(letter);
        setTimeout(() => {
            hideLetterPreview();
        }, 1000);
    }

    setupLetterObserver() {
        const letterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const letter = entry.target.dataset.letter;
                const buttons = document.querySelectorAll(`.quick-jump-btn[data-letter="${letter}"]`);
                
                buttons.forEach(button => {
                    if (entry.isIntersecting) {
                        document.querySelectorAll('.quick-jump-btn').forEach(btn => {
                            btn.classList.remove('btn-primary', 'scale-110', 'shadow-lg');
                        });
                        button.classList.add('btn-primary', 'scale-110', 'shadow-lg');
                        button.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
                    }
                });
            });
        }, { 
            threshold: 0.2,
            rootMargin: '-80px 0px -60% 0px'
        });

        document.querySelectorAll('.skill-group').forEach(group => {
            letterObserver.observe(group);
        });
    }
}

// Modify the initialization code
document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Initialize helpers
        window.skillIconsHelper = new SkillIconsHelper();
        await window.skillIconsHelper.initialize();
        
        // Initialize other components
        await window.skillsHelper.initialize();
        
        // Initialize skill select after helpers are ready
        window.skillSelectManager = new SkillSelectManager();
        const skillSelect = document.getElementById('skills-select');
        if (skillSelect) {
            const tomSelect = window.skillSelectManager.initializeSelect('#skills-select');
            
            // Force refresh icons after initialization
            requestAnimationFrame(async () => {
                const dropdown = document.querySelector('.ts-dropdown');
                if (dropdown) {
                    await window.skillIconsHelper.updateIcons();
                }
            });

            // Watch for theme changes
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            mediaQuery.addEventListener('change', (e) => {
                window.skillSelectManager.handleThemeChange(tomSelect, e.matches);
            });
        }

        // Initialize skills modal
        window.skillsManager = new SkillsModalManager();

        // Make functions globally available
        window.jumpToLetter = (letter) => window.skillsManager.jumpToLetter(letter);
        window.applySelectedSkills = () => window.skillsManager.applySelectedSkills();
        window.showLetterPreview = showLetterPreview;
        window.hideLetterPreview = hideLetterPreview;

    } catch (error) {
        console.error('Failed to initialize application:', error);
    }
});

function showLetterPreview(letter) {
    const preview = document.getElementById('letter-preview');
    if (!preview) return;
    
    preview.textContent = letter;
    preview.classList.remove('hidden', 'scale-0');
    preview.classList.add('scale-100');
}

function hideLetterPreview() {
    const preview = document.getElementById('letter-preview');
    if (!preview) return;
    
    preview.classList.remove('scale-100');
    preview.classList.add('scale-0');
}

function renderSelectedSkills() {
    skillsContainer.innerHTML = '';
    skillsInput.value = JSON.stringify([...selectedSkills]);

    selectedSkills.forEach(async skillName => {
        const checkbox = document.querySelector(`input[value="${skillName}"]`);
        if (!checkbox) return;

        const skillData = JSON.parse(checkbox.dataset.skill);
        const tag = document.createElement('div');
        tag.className = 'flex items-center gap-2 bg-base-200 px-3 py-1 rounded-full group hover:bg-base-300 transition-colors';
        
        // Create a placeholder for the icon
        const iconPlaceholder = document.createElement('div');
        iconPlaceholder.className = 'w-5 h-5 flex items-center justify-center';
        
        tag.innerHTML = `
            <span>${skillData.name}</span>
            <button type="button" 
                    onclick="removeSkill('${skillData.name}')" 
                    class="btn btn-xs btn-ghost btn-circle opacity-50 group-hover:opacity-100">
                <iconify-icon icon="heroicons:x-mark-20-solid"></iconify-icon>
            </button>
        `;
        tag.insertAdjacentElement('afterbegin', iconPlaceholder);
        
        // Add to container immediately
        skillsContainer.appendChild(tag);
        
        // Load and insert icon asynchronously
        const icon = document.createElement('iconify-icon');
        icon.setAttribute('width', '20');
        icon.setAttribute('height', '20');
        await window.skillIconsHelper.refreshIconElement(icon, skillData.icon);
        iconPlaceholder.replaceWith(icon);
    });
}