function setupHover(element, callback) {
    let cleanup = null;
    
    const start = () => {
        if (cleanup) cleanup();
        cleanup = callback();
    };
    
    const end = () => {
        if (cleanup) {
            cleanup();
            cleanup = null;
        }
    };
    
    element.addEventListener('mouseenter', start);
    element.addEventListener('mouseleave', end);
    element.addEventListener('touchstart', start, { passive: true });
    element.addEventListener('touchend', end);
    element.addEventListener('touchcancel', end);

    return () => {
        element.removeEventListener('mouseenter', start);
        element.removeEventListener('mouseleave', end);
        element.removeEventListener('touchstart', start);
        element.removeEventListener('touchend', end);
        element.removeEventListener('touchcancel', end);
        if (cleanup) cleanup();
    };
}

function isIconifyReady() {
    return typeof iconifyIcon !== 'undefined' && document.createElement('iconify-icon').constructor !== HTMLElement;
}

class SkillIconsHelper {
    constructor() {
        this.darkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        this.watchThemeChanges();
        this.initialized = true;
        this.initializationAttempts = 0;
        this.iconMappings = {
            'JavaScript': 'logos:javascript',
            'Python': 'logos:python',
            'Java': 'logos:java',
            'React': 'logos:react',
            'Angular': 'logos:angular-icon',
            'Vue': 'logos:vue',
            'Node.js': 'logos:nodejs-icon',
            'TypeScript': 'logos:typescript-icon',
            'PHP': 'logos:php',
            'Ruby': 'logos:ruby',
            'Go': 'logos:go',
            'Rust': 'logos:rust',
            'C++': 'logos:c-plusplus',
            'C#': 'logos:c-sharp',
            'Swift': 'logos:swift',
            'Kotlin': 'logos:kotlin-icon',
            'Docker': 'logos:docker-icon',
            'Kubernetes': 'logos:kubernetes',
            'AWS': 'logos:aws',
            'Azure': 'logos:microsoft-azure',
            'Git': 'logos:git-icon',
            'MongoDB': 'logos:mongodb-icon',
            'PostgreSQL': 'logos:postgresql',
            'MySQL': 'logos:mysql',
            'Redis': 'logos:redis',
            'HTML': 'logos:html-5',
            'CSS': 'logos:css-3',
            'Sass': 'logos:sass',
            'GraphQL': 'logos:graphql',
            'Django': 'logos:django-icon',
            'Flask': 'logos:flask',
            'Spring': 'logos:spring-icon',
            'Linux': 'logos:linux-tux',
            'Jenkins': 'logos:jenkins',
            'Webpack': 'logos:webpack',
            'npm': 'logos:npm-icon',
            'yarn': 'logos:yarn'
        };
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

    async refreshIconElement(element, skillName, darkIconName = null) {
        if (!element || !skillName) return;
        
        try {
            element.style.display = 'inline-block';
            element.style.visibility = 'visible';
            
            // Use skills-icons mapping or fallback to generic icon
            const icon = this.iconMappings[skillName] || 'octicon:code-16';
            
            element.setAttribute('icon', icon);
            element.setAttribute('width', '20');
            element.setAttribute('height', '20');

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
            console.warn(`Failed to refresh icon for skill: ${skillName}`);
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

    getIconForSkill(skillName) {
        return this.iconMappings[skillName] || 'octicon:code-16';
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

class LetterMagnifier {
    constructor() {
        // Find magnifier elements inside modal instead of creating new ones
        this.magnifier = document.querySelector('.modal .letter-magnifier');
        this.preview = document.querySelector('.modal .letter-preview');
    }

    // Remove create methods since elements exist in DOM
    createMagnifier() {}
    setupLetterPreview() {}

    showMagnifier(letter, position) {
        this.magnifier.textContent = letter;
        this.magnifier.style.left = `${position.x}px`;
        this.magnifier.style.top = `${position.y}px`;
        this.magnifier.style.transform = 'translateX(-80px) scale(1)';
        this.magnifier.style.opacity = '1';
    }

    hideMagnifier() {
        this.magnifier.style.transform = 'translateX(0) scale(0.8)';
        this.magnifier.style.opacity = '0';
    }

    showPreview(letter) {
        this.preview.textContent = letter;
        this.preview.classList.remove('hidden');
        requestAnimationFrame(() => {
            this.preview.classList.add('visible');
        });
    }

    hidePreview() {
        this.preview.classList.remove('visible');
        setTimeout(() => this.preview.classList.add('hidden'), 150);
    }
}

class SkillsModalManager {
    constructor() {
        // Add isDarkMode to the instance
        this.isDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Watch for theme changes
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            this.isDarkMode = e.matches;
            this.renderSelectedSkills(); // Re-render when theme changes
        });

        // Initialize properties
        this.selectedSkills = new Set();
        this.skillsContainer = document.getElementById('selected-skills');
        this.skillsInput = document.getElementById('skills-input');
        this.skillSearch = document.getElementById('skill-search');
        this.modal = document.getElementById('skills-modal');
        this.iconHelper = window.skillIconsHelper;
        this.letterGroups = document.querySelectorAll('.skill-group[data-letter]');
        this.quickJump = document.querySelector('.quick-jump-container');
        this.magnifier = new LetterMagnifier();
        this.placeholder = document.getElementById('skills-placeholder'); // Add this line
        
        // Add container reference for mobile CTA
        this.formSection = document.querySelector('.form-section');
        
        // Bind methods to preserve 'this' context
        this.handleSearch = this.handleSearch.bind(this);
        this.handleModalShow = this.handleModalShow.bind(this);
        this.updateActiveState = this.updateActiveState.bind(this);
        this.jumpToLetter = this.jumpToLetter.bind(this);
        this.magnifyLetterGroup = this.magnifyLetterGroup.bind(this);
        this.resetLetterGroup = this.resetLetterGroup.bind(this);
        this.showLetterPreview = this.showLetterPreview.bind(this);
        this.hidePreview = this.hidePreview.bind(this);
        this.handleCancel = this.handleCancel.bind(this);
        
        // Initialize components
        this.initializeModal();
        this.setupLetterMagnification();
        this.setupLetterNavigation();
        this.setupLetterEffects();
    }

    updateActiveState(letter) {
        if (!letter) return;
        
        requestAnimationFrame(() => {
            for (const btn of document.querySelectorAll('.quick-letter')) {
                btn.classList.toggle('active', btn.dataset.letter === letter);
            }
            
            this.showLetterPreview(letter);
        });
    }

    hidePreview() {
        if (this.magnifier) {
            this.magnifier.hidePreview();
        }
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
        this.setupLetterNavigation();
    }

    handleSearch(e) {
        const query = e.target.value.toLowerCase();
        const hasQuery = query.length > 0;

        // Filter skills and track if any skills are visible in each group
        this.letterGroups.forEach(group => {
            const heading = group.querySelector('.sticky');
            const labels = group.querySelectorAll('label');
            let hasVisibleSkills = false;

            // Check and hide/show skills
            labels.forEach(label => {
                const skillName = label.querySelector('span').textContent.toLowerCase();
                const matches = skillName.includes(query);
                label.style.display = matches ? '' : 'none';
                if (matches) hasVisibleSkills = true;
            });

            // Hide/show the entire group based on whether it has visible skills
            group.style.display = hasVisibleSkills ? '' : 'none';
            if (heading) heading.style.display = hasQuery ? 'none' : 'block';
        });

        // Toggle quick jump visibility
        if (this.quickJump) {
            this.quickJump.style.display = hasQuery ? 'none' : 'block';
        }
    }

    resetModalState() {
        // Clear search
        if (this.skillSearch) {
            this.skillSearch.value = '';
            
            // Show everything
            this.letterGroups.forEach(group => {
                group.style.display = '';
                const heading = group.querySelector('.sticky');
                if (heading) heading.style.display = 'block';
                group.querySelectorAll('label').forEach(label => {
                    label.style.display = '';
                });
            });

            if (this.quickJump) {
                this.quickJump.style.display = 'block';
            }
        }

        // Reset checkboxes to match current selection
        document.querySelectorAll('#skills-modal input[type="checkbox"]').forEach(cb => {
            cb.checked = this.selectedSkills.has(cb.value);
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
        this.resetModalState();
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

        // Show/hide placeholder based on selected skills
        if (this.placeholder) {
            if (this.selectedSkills.size === 0) {
                this.placeholder.style.display = 'flex';
            } else {
                this.placeholder.style.display = 'none';
            }
        }

        const badgeTypes = ['badge-primary', 'badge-accent', 'badge-neutral'];
        const skillBadgeTypes = JSON.parse(localStorage.getItem('skillBadgeTypes') || '{}');

        this.selectedSkills.forEach(skillName => {
            const checkbox = document.querySelector(`input[value="${skillName}"]`);
            if (!checkbox) return;

            const skillData = JSON.parse(checkbox.dataset.skill);
            const icon = this.isDarkMode && skillData.icon_dark ? skillData.icon_dark : skillData.icon;
            
            // Use stored badge type or create new one
            if (!skillBadgeTypes[skillName]) {
                skillBadgeTypes[skillName] = badgeTypes[Math.floor(Math.random() * badgeTypes.length)];
                localStorage.setItem('skillBadgeTypes', JSON.stringify(skillBadgeTypes));
            }
            
            const badgeType = skillBadgeTypes[skillName];
            
            const badge = document.createElement('div');
            badge.className = `badge ${badgeType} badge-lg gap-1 pr-0`; 
            badge.innerHTML = `
                <iconify-icon icon="${icon}" 
                             data-icon="${skillData.icon}"
                             data-icon-dark="${skillData.icon_dark || skillData.icon}"
                             class="text-${badgeType.split('-')[1]}-content"
                             width="16"></iconify-icon>
                <span class="font-medium text-${badgeType.split('-')[1]}-content">${skillData.name}</span>
                <button type="button" 
                        class="btn btn-ghost btn-xs btn-square h-full rounded-l-none hover:bg-opacity-20">
                    <iconify-icon icon="heroicons:x-mark-20-solid" 
                                class="text-xs text-${badgeType.split('-')[1]}-content">
                    </iconify-icon>
                </button>
            `;
            
            // Add click handler
            const removeBtn = badge.querySelector('button');
            removeBtn.addEventListener('click', () => this.removeSkill(skillName));
            
            this.skillsContainer.appendChild(badge);
        });

        // Toggle mobile CTA visibility based on skills
        if (this.formSection) {
            this.formSection.classList.toggle('has-skills', this.selectedSkills.size > 0);
        }
    }

    jumpToLetter(letter, smooth = true) {
        const group = document.querySelector(`.skill-group[data-letter="${letter}"]`);
        if (!group) return;

        const container = document.querySelector('.modal-box .overflow-y-auto');
        const header = document.querySelector('.modal-box .flex-none');
        const offset = header ? header.offsetHeight : 0;

        container.classList.toggle('smooth-scroll', smooth);
        
        requestAnimationFrame(() => {
            const targetScroll = group.offsetTop - offset - 8;
            container.scrollTo({
                top: targetScroll,
                behavior: smooth ? 'smooth' : 'instant'
            });
            
            // Update letter states with smoother transitions
            this.updateLetterStates(letter);
        });

        // Remove smooth scroll class after animation
        if (smooth) {
            setTimeout(() => {
                container.classList.remove('smooth-scroll');
            }, 300);
        }
    }

    updateLetterStates(activeLetter) {
        document.querySelectorAll('.quick-letter').forEach(btn => {
            const letter = btn.dataset.letter;
            btn.classList.remove('active', 'adjacent');
            
            if (letter === activeLetter) {
                btn.classList.add('active');
            } else if (
                letter === String.fromCharCode(activeLetter.charCodeAt(0) - 1) ||
                letter === String.fromCharCode(activeLetter.charCodeAt(0) + 1)
            ) {
                btn.classList.add('adjacent');
            }
        });
    }

    setupLetterNavigation() {
        document.querySelectorAll('.quick-letter').forEach(btn => {
            // Handle hover
            btn.addEventListener('mouseenter', () => {
                const letter = btn.dataset.letter;
                this.jumpToLetter(letter, false); // Instant jump on hover
            });

            // Handle touch with passive option
            btn.addEventListener('touchstart', (e) => {
                const letter = btn.dataset.letter;
                // Store touch position for potential scroll prevention
                this._touchStartY = e.touches[0].clientY;
                this.jumpToLetter(letter, true);
            }, { passive: true });

            // Handle click
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const letter = btn.dataset.letter;
                this.jumpToLetter(letter, true); // Smooth scroll on click
            });
        });
    }

    setupLetterObserver() {
        const letterObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (!entry.isIntersecting) return;
                
                const letter = entry.target.dataset.letter;
                if (!letter) return;

                requestAnimationFrame(() => {
                    this.updateActiveState(letter);
                });
            });
        }, { 
            threshold: 0.5,  // Increased threshold for better accuracy
            rootMargin: '-80px 0px -60% 0px'
        });

        document.querySelectorAll('.skill-group').forEach(group => {
            letterObserver.observe(group);
        });
    }

    setupLetterMagnification() {
        const letters = document.querySelectorAll('.quick-letter');
        const container = document.querySelector('.quick-letters-list');
        const modalBox = document.querySelector('.modal-box');
        
        letters.forEach((letter, index) => {
            setupHover(letter, () => {
                const rect = letter.getBoundingClientRect();
                const containerRect = container.getBoundingClientRect();
                const modalRect = modalBox.getBoundingClientRect();
                
                // Update active state immediately
                this.updateActiveState(letter.dataset.letter);

                // Calculate if letter is near bottom of modal
                const isNearBottom = rect.bottom > (modalRect.bottom - 100);
                
                const position = {
                    x: containerRect.left - 16,
                    y: Math.min(
                        rect.top + (rect.height / 2),
                        modalRect.bottom - 50 // Keep magnifier inside modal
                    )
                };
                
                this.magnifier.showMagnifier(letter.dataset.letter, position);
                this.magnifyLetterGroup(letters, index);
                this.magnifier.showPreview(letter.dataset.letter);

                // Scroll handling for bottom letters
                if (isNearBottom) {
                    const scrollContainer = modalBox.querySelector('.overflow-y-auto');
                    if (scrollContainer) {
                        scrollContainer.scrollTo({
                            top: scrollContainer.scrollHeight,
                            behavior: 'smooth'
                        });
                    }
                }

                return () => {
                    this.resetLetterGroup(letters, index);
                    this.magnifier.hideMagnifier();
                    this.magnifier.hidePreview();
                };
            });
        });
    }

    magnifyLetterGroup(letters, index) {
        const mainLetter = letters[index];
        if (mainLetter) {
            mainLetter.classList.add('letter-magnified', 'letter-primary');
        }
        
        [-1, 1].forEach(offset => {
            const neighbor = letters[index + offset];
            if (neighbor) {
                neighbor.classList.add('letter-neighbor');
            }
        });
    }

    resetLetterGroup(letters, index) {
        const affectedIndexes = [index - 1, index, index + 1];
        affectedIndexes.forEach(i => {
            const letter = letters[i];
            if (letter) {
                letter.classList.remove('letter-magnified', 'letter-primary', 'letter-neighbor');
            }
        });
    }

    setupLetterEffects() {
        const letters = document.querySelectorAll('.quick-letter');
        const container = document.querySelector('.quick-letters-list');
        if (!container || !letters.length) return;

        let currentLetter = null;
        let lastScrollTime = 0;
        const scrollDebounce = 100; // ms

        // Handle scroll events
        const scrollContainer = document.querySelector('.modal-box .overflow-y-auto');
        if (scrollContainer) {
            scrollContainer.addEventListener('scroll', () => {
                const now = Date.now();
                if (now - lastScrollTime < scrollDebounce) return;
                lastScrollTime = now;

                const visibleGroup = this.findVisibleLetterGroup();
                if (visibleGroup && visibleGroup.dataset.letter !== currentLetter) {
                    currentLetter = visibleGroup.dataset.letter;
                    this.updateLetterStates(currentLetter);
                }
            }, { passive: true });
        }

        // Touch handling with passive events
        container.addEventListener('touchstart', (e) => {
            this._touchStartY = e.touches[0].clientY;
        }, { passive: true });

        container.addEventListener('touchmove', (e) => {
            const letter = this.findLetterAtPosition(e.touches[0].clientY);
            if (letter) this.jumpToLetter(letter, false);
        }, { passive: true });

        container.addEventListener('touchend', () => {
            this._touchStartY = null;
        }, { passive: true });
    }

    findLetterAtPosition(y) {
        const letters = document.querySelectorAll('.quick-letter');
        for (const letter of letters) {
            const rect = letter.getBoundingClientRect();
            if (y >= rect.top && y <= rect.bottom) {
                return letter.dataset.letter;
            }
        }
        return null;
    }

    handleLetterTouchStart(e) {
        e.preventDefault();
        const letter = this.findLetterAtPosition(e.touches[0].clientY);
        if (letter) this.jumpToLetter(letter, true);
    }

    findVisibleLetterGroup() {
        const groups = document.querySelectorAll('.skill-group');
        const containerTop = document.querySelector('.modal-box').getBoundingClientRect().top;
        
        for (const group of groups) {
            const rect = group.getBoundingClientRect();
            if (rect.top >= containerTop && rect.bottom > containerTop) {
                return group;
            }
        }
        return null;
    }

    updateLetterStates(activeLetter) {
        document.querySelectorAll('.quick-letter').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.letter === activeLetter);
        });
    }

    showLetterPreview(letter) {
        if (!this.magnifier) return;
        this.magnifier.showPreview(letter);
        
        // Create or update letter highlight effect
        const group = document.querySelector(`.skill-group[data-letter="${letter}"]`);
        if (group) {
            let highlight = group.querySelector('.letter-group-highlight');
            if (!highlight) {
                highlight = document.createElement('div');
                highlight.className = 'letter-group-highlight';
                group.insertBefore(highlight, group.firstChild);
            }
            highlight.classList.add('visible');
            setTimeout(() => highlight.classList.remove('visible'), 500);
        }
    }

    handleCancel(e) {
        e.preventDefault();
        // Reset form validation states
        const form = e.target.closest('form');
        if (form) {
            form.classList.remove('was-validated');
            // Remove any validation messages
            form.querySelectorAll('.text-error').forEach(el => el.textContent = '');
            form.reset();
        }
        
        // Reset modal state
        this.resetModalState();
        
        // Close modal if open
        if (this.modal?.open) {
            this.modal.close();
        }

        // Navigate back or to list page
        window.location.href = e.target.href;
        return false;
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
        window.jumpToLetter = (letter) => window.skillsManager.jumpToLetter(letter, true);
        window.applySelectedSkills = () => window.skillsManager.applySelectedSkills();
        window.showLetterPreview = showLetterPreview;
        window.hideLetterPreview = hideLetterPreview;

    } catch (error) {
        console.error('Failed to initialize application:', error);
    }
});

function showLetterPreview(letter) {
    if (!window.skillsManager?.magnifier) return;
    window.skillsManager.magnifier.showPreview(letter);
}

function hideLetterPreview() {
    if (!window.skillsManager?.magnifier) return;
    window.skillsManager.magnifier.hidePreview();
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

    const quickLettersContainer = document.querySelector('.quick-letters');
    const quickLetters = document.querySelectorAll('.quick-letter');
    const lens = document.querySelector('.lens-overlay');
    const lensWidth = parseInt(getComputedStyle(document.documentElement).getPropertyValue('--lens-width'));

    lens.addEventListener('animationiteration', () => {
        // Reset classes if needed at each iteration
        quickLetters.forEach(letter => letter.classList.remove('in-focus'));
    });

    lens.addEventListener('animationstart', () => {
        // Optionally handle animation start
    });

    lens.addEventListener('animationstart', () => {
        // Update the focus class during animation
        const animationDuration = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--animation-speed')) * 1000;
        quickLetters.forEach((letter, index) => {
            const delay = (animationDuration / quickLetters.length) * index;
            setTimeout(() => {
                letter.classList.add('in-focus');
                setTimeout(() => {
                    letter.classList.remove('in-focus');
                }, animationDuration / quickLetters.length);
            }, delay);
        });
    });
}

// Add global cancel handler
function handleCancel(e) {
    // Prevent form validation
    const form = e.target.closest('form');
    if (form) {
        form.noValidate = true;
        setTimeout(() => form.noValidate = false, 100);
    }
    
    // Handle any open modals
    const modal = document.querySelector('dialog[open]');
    if (modal) {
        modal.close();
    }

    return true; // Allow normal navigation
}

// Add to global scope
window.handleCancel = handleCancel;
