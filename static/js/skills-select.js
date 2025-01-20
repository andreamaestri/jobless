// Wait for both DOM and Alpine.js to be ready
document.addEventListener('alpine:init', () => {
    if (!window.Alpine) {
        console.error('Alpine.js not loaded');
        return;
    }
    // Icon loading utility with cache and better error handling
    const iconCache = new Map();
    const loadIcon = (icon, name) => {
        const defaultIcon = 'heroicons:squares-2x2';
        
        // Check if we have a mapping for this skill name
        if (name && window.ICON_NAME_MAPPING && window.ICON_NAME_MAPPING[name]) {
            icon = window.ICON_NAME_MAPPING[name];
        }
        
        if (!icon) return defaultIcon;
        
        if (iconCache.has(icon)) {
            return iconCache.get(icon);
        }

        // Set default initially
        iconCache.set(icon, defaultIcon);
        
        // Check if icon exists in Iconify
        if (window.Iconify) {
            try {
                if (window.Iconify.iconExists(icon)) {
                    iconCache.set(icon, icon);
                } else {
                    window.Iconify.loadIcon(icon);
                    // Don't wait for the load, keep default for now
                }
            } catch (error) {
                console.warn(`Error checking icon existence: ${icon}`, error);
            }
        }

        return iconCache.get(icon);
    };

    // Initialize skill icons collection
    const preloadIcons = () => {
        if (window.ICON_NAME_MAPPING) {
            const uniqueIcons = new Set(Object.values(window.ICON_NAME_MAPPING));
            if (window.Iconify) {
                // Load icons without expecting a Promise
                window.Iconify.loadIcons([...uniqueIcons]);
                
                // Periodically check for loaded icons
                const checkLoaded = setInterval(() => {
                    const allLoaded = [...uniqueIcons].every(icon => 
                        window.Iconify.iconExists(icon)
                    );
                    if (allLoaded) {
                        clearInterval(checkLoaded);
                        if (skillSelect) {
                            skillSelect.refreshOptions();
                        }
                    }
                }, 100);

                // Clear interval after 5 seconds to prevent infinite checking
                setTimeout(() => clearInterval(checkLoaded), 5000);
            }
        }
    };

    // Preload icons when component initializes
    preloadIcons();

    const select = document.getElementById('skills-select');
    if (!select) return;

    const skillSelect = new TomSelect(select, {
        valueField: 'name',
        labelField: 'name',
        searchField: ['name'],
        plugins: ['remove_button'],
        maxItems: 10,
        persist: false,
        createFilter: null,
        preload: true,
        
        // Dropdown configuration
        dropdownParent: 'body',
        maxOptions: 200,
        hideSelected: true,
        closeAfterSelect: false,
        openOnFocus: true,
        
        // Search configuration
        searchConjunction: 'and',
        sortField: [
            { field: 'letter' },
            { field: 'name' }
        ],

        // Custom rendering with dark mode support
        render: {
            option: function(data, escape) {
                const icon = loadIcon(data.icon_dark || data.icon, data.name);
                return `<div class="flex items-center gap-4 p-2 transition-all hover:pl-4">
                    <div class="w-8 h-8 flex items-center justify-center bg-base-200 rounded-lg">
                        <iconify-icon icon="${escape(icon)}" 
                                     class="text-xl text-base-content/70"
                                     onload="this.classList.add('is-loaded')"
                                     onerror="this.setAttribute('icon', 'heroicons:squares-2x2')"></iconify-icon>
                    </div>
                    <span class="font-medium">${escape(data.name)}</span>
                </div>`;
            },
            item: function(data, escape) {
                const icon = loadIcon(data.icon_dark || data.icon, data.name);
                return `<div class="flex items-center gap-2 bg-primary/10 text-primary rounded-lg px-3 py-1.5">
                    <iconify-icon icon="${escape(icon)}" 
                                 class="text-lg"
                                 onload="this.classList.add('is-loaded')"
                                 onerror="this.setAttribute('icon', 'heroicons:squares-2x2')"></iconify-icon>
                    <span>${escape(data.name)}</span>
                </div>`;
            },
            optgroup_header: function(data, escape) {
                return `<div class="sticky top-0 z-10 px-3 py-2 text-lg font-bold text-primary bg-base-100/95 backdrop-blur-sm">
                    ${escape(data.label)}
                </div>`;
            },
            no_results: function(data, escape) {
                return `<div class="p-4 text-center text-base-content/70">
                    No skills found for "${escape(data.input)}"
                </div>`;
            },
            loading: function() {
                return `<div class="p-4 text-center">
                    <span class="loading loading-spinner loading-sm"></span>
                </div>`;
            },
            dropdown: function() {
                return `<div class="ts-dropdown">
                    <div class="ts-dropdown-content"></div>
                    <div class="p-2 border-t border-base-200">
                        <button type="button" 
                                class="btn btn-ghost btn-sm w-full gap-2"
                                onclick="window.dispatchEvent(new CustomEvent('open-skills-modal', {
                                    detail: { 
                                        selectedSkills: window.skillSelect.items.map(name => ({
                                            name: name,
                                            ...window.skillSelect.options[name]
                                        }))
                                    }
                                }))">
                            <iconify-icon icon="heroicons:squares-plus"></iconify-icon>
                            Manage Skills
                        </button>
                    </div>
                </div>`;
            }
        },

        load: function(query, callback) {
            const url = new URL('/jobs/skills/autocomplete/', window.location.origin);
            url.searchParams.set('q', query || '');
            url.searchParams.set('all', 'true');
            
            fetch(url)
                .then(response => response.ok ? response.json() : Promise.reject(response))
                .then(json => {
                    // Clear existing options first
                    this.clearOptions();
                    if (!json.results || !Array.isArray(json.results)) {
                        throw new Error('Invalid response format');
                    }

                    const optgroups = json.results.map(group => ({
                        value: group.letter,
                        label: group.letter,
                        $order: group.letter.charCodeAt(0)
                    }));
                    
                    const options = json.results.flatMap(group => 
                        group.skills.map(skill => ({
                            ...skill,
                            letter: group.letter,
                            icon: loadIcon(skill.icon_dark || skill.icon, skill.name)
                        }))
                    );

                    callback(options, optgroups);
                })
                .catch(error => {
                    console.error('Error loading skills:', error);
                    if (Alpine && Alpine.store('toastManager')) {
                        Alpine.store('toastManager').show(
                            'Failed to load skills. Please try again.',
                            'error'
                        );
                    }
                    callback();
                });
        },

        // Input change handling
        onChange: function(values) {
            const selectedSkills = this.items.map(value => {
                const item = this.options[value];
                return {
                    name: item.name,
                    icon: item.icon,
                    icon_dark: item.icon_dark
                };
            });
            
            // Update hidden input
            const skillsInput = document.getElementById('skills-input');
            if (skillsInput) {
                skillsInput.value = JSON.stringify(selectedSkills);
            }
            
            // Update skills count
            const skillsCount = document.getElementById('skills-count');
            if (skillsCount) {
                skillsCount.textContent = `${selectedSkills.length} selected`;
            }
        }
    });

    // Expose skillSelect to window for modal interaction
    window.skillSelect = skillSelect;

    // Force initial load of all skills
    skillSelect.load('');

    // Event handlers for better UX
    skillSelect.on('dropdown_open', function(dropdown) {
        // Ensure dropdown is visible in viewport
        if (dropdown) {
            const rect = dropdown.getBoundingClientRect();
            const viewHeight = Math.max(document.documentElement.clientHeight, window.innerHeight);
            if (rect.bottom > viewHeight) {
                dropdown.style.top = `${viewHeight - rect.height - 20}px`;
            }
        }
    });

    skillSelect.on('item_add', function(value, item) {
        // Show feedback when skill is added
        item.classList.add('animate-scale-in');
        
        // Update form state
        const form = document.getElementById('job-form');
        if (form) {
            form.classList.add('has-skills');
        }
    });

    skillSelect.on('item_remove', function(value) {
        // Update form state when no skills are selected
        const form = document.getElementById('job-form');
        if (form && skillSelect.items.length === 0) {
            form.classList.remove('has-skills');
        }
    });

    skillSelect.on('clear', function() {
        // Reset form state
        const form = document.getElementById('job-form');
        if (form) {
            form.classList.remove('has-skills');
        }
    });

    skillSelect.on('type', function(str) {
        // Show loading state while searching
        const wrapper = select.closest('.ts-wrapper');
        if (wrapper) {
            wrapper.classList.toggle('is-searching', str.length > 0);
        }
    });

    // Replace duplicate event listeners with a single one
    document.removeEventListener('skills-updated', window.skillsUpdateHandler);
    window.skillsUpdateHandler = function(event) {
        const updatedSkills = event.detail;
        
        // Clear existing selections without triggering events
        skillSelect.clear(true);
        skillSelect.clearOptions();
        
        // Add new options
        updatedSkills.forEach(skill => {
            skillSelect.addOption({
                name: skill.name,
                icon: skill.icon,
                icon_dark: skill.icon_dark,
                letter: skill.name[0].toUpperCase()
            });
            
            // Select the option
            skillSelect.addItem(skill.name);
        });

        // Update hidden input
        const skillsInput = document.getElementById('skills-input');
        if (skillsInput) {
            skillsInput.value = JSON.stringify(updatedSkills);
        }

        // Trigger change event
        skillSelect.trigger('change');
    };
    
    document.addEventListener('skills-updated', window.skillsUpdateHandler);
});
