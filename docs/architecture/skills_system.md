**Improved Skills System Architecture**

## Overview

This document outlines the architecture for an improved skills system designed for a job platform. The system provides a robust and flexible way to manage job-related skills, incorporating a hierarchical structure, proficiency levels, and enhanced user interface elements. It leverages the `django-tagulous` library for efficient tag management and offers advanced features for both job posters and candidates.

## Goals

*   **Hierarchical Skill Organization:** Implement a tree-like structure to categorize skills into logical groups and sub-groups.
*   **Proficiency Levels:** Allow job posters to specify the required proficiency level for each skill.
*   **User-Friendly Skill Selection:** Provide an intuitive and interactive interface for selecting skills and specifying proficiency.
*   **Efficient Searching and Filtering:** Enable efficient searching and filtering of skills and jobs based on skills and proficiency.
*   **Maintainability and Extensibility:** Design a system that is easy to maintain, extend, and adapt to future needs.
*   **Data Integrity:** Ensure data consistency and prevent invalid skill/proficiency combinations.

## Core Components

### 1. `SkillTreeModel` (Model)

This model represents a skill within the system. It utilizes `django-tagulous`'s `TagTreeModel` to create a hierarchical structure.

```python
from tagulous.models import TagTreeModel

class SkillTreeModel(TagTreeModel):
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Iconify icon code (e.g., mdi:language-python)"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description of the skill"
    )

    class TagMeta:
        tree = True  # Enable hierarchical structure
        # Use numeric paths for faster queries
        autocomplete_limit = 1000 # Prevent it from trying to load every skill at once

    def __str__(self):
        return self.label
```

**Fields:**

*   `icon`: Stores the Iconify icon code for the skill (e.g., `mdi:language-python`).
*   `description`: Provides a detailed description of the skill.
*   `name`: The unique name of the skill (automatically managed by `TagTreeModel`).
*   `path`: The hierarchical path of the skill (e.g., `000100020003`), used for efficient querying.
*   `label`: The display label for the skill.
*   `parent`: A foreign key to the parent skill in the hierarchy.
*   `children`: A reverse relation to child skills.

**Example Skill Hierarchy:**

```
- Programming (0001)
  - Languages (00010001)
    - Python (000100010001)
    - JavaScript (000100010002)
  - Frameworks (00010002)
    - Django (000100020001)
    - React (000100020002)
  - Databases (00010003)
    - PostgreSQL (000100030001)
    - MySQL (000100030002)
- Design (0002)
  - UI/UX (00020001)
  - Graphic Design (00020002)
```

### 2. `JobSkill` (Model)

This model represents the relationship between a `JobPosting` and a `SkillTreeModel`, including the required proficiency level.

```python
class JobSkill(models.Model):
    PROFICIENCY_LEVELS = [
        ('required', 'Required'),
        ('preferred', 'Preferred'),
        ('bonus', 'Nice to Have')
    ]

    job = models.ForeignKey('JobPosting', on_delete=models.CASCADE, related_name="job_skills")
    skill = models.ForeignKey(SkillTreeModel, on_delete=models.CASCADE, related_name="job_skills")
    proficiency = models.CharField(
        max_length=20,
        choices=PROFICIENCY_LEVELS,
        default='required'
    )

    class Meta:
        unique_together = ['job', 'skill']
        verbose_name_plural = "Job Skills"

    def __str__(self):
        return f"{self.job.title} - {self.skill.label} ({self.proficiency})"
```

**Fields:**

*   `job`: A foreign key to the `JobPosting`.
*   `skill`: A foreign key to the `SkillTreeModel`.
*   `proficiency`: The required proficiency level for the skill (e.g., "required", "preferred", "bonus").

### 3. `JobPosting` (Model - Enhancement)

The `JobPosting` model is enhanced to use the `JobSkill` model for managing skills.

```python
class JobPosting(models.Model):
    # ... other fields ...

    skills = models.ManyToManyField(
        SkillTreeModel,
        through='JobSkill',
        related_name='jobs',
        blank=True,
        help_text="Skills associated with this job posting"
    )

    # ... other fields ...
```

### 4. `JobPostingForm` (Form)

This form is used to create and edit job postings, including the skill selection.

```python
class JobPostingForm(forms.ModelForm):
    skills = forms.CharField(
        widget=SkillTreeWidget(attrs={'class': 'skill-tree-select'}),
        required=False  # Skills are optional
    )

    class Meta:
        model = JobPosting
        fields = ['title', ..., 'skills'] # Include other fields as needed

    def clean_skills(self):
        # ... (Implementation detailed in the Frontend section) ...

    def save(self, commit=True):
        # ... (Implementation detailed in the Frontend section) ...
```

*   The `skills` field uses a `CharField` to store a JSON representation of selected skills and their proficiencies.
*   The `SkillTreeWidget` is used to render the interactive skill tree.
*   `clean_skills()`: This method validates the submitted skill data, ensuring that the skill IDs are valid and that the proficiency levels are correct.
*   `save()`: This method handles saving the `JobPosting` and creating/updating the related `JobSkill` instances.

## Frontend Components

### 1. `SkillTreeWidget` (Django Widget)

This widget renders the HTML and includes the necessary CSS and JavaScript for the interactive skill tree.

```python
class SkillTreeWidget(forms.SelectMultiple):
    template_name = 'jobs/widgets/skill_tree_widget.html'

    class Media:
        css = {
            'all': ['css/skill-tree.css']
        }
        js = ['js/skill-tree-widget.js']
```

*   `template_name`: Specifies the template to use for rendering the widget (`skill_tree_widget.html`).
*   `Media`: Defines the required CSS and JavaScript assets.

### 2. `skill_tree_widget.html` (Template)

This template defines the structure of the skill tree widget.

```html
{% comment %} jobs/widgets/skill_tree_widget.html {% endcomment %}
<div class="skill-tree-widget" id="{{ widget.attrs.id }}">
    <div class="skill-search">
        <input type="text"
               class="skill-search-input"
               placeholder="Search skills...">
    </div>

    <div class="skill-categories" data-categories="{{ categories_json|safe }}">
        {# Categories will be rendered here by JavaScript #}
    </div>

    {# Hidden input for form submission #}
    <input type="hidden"
           name="{{ widget.name }}"
           value="{{ widget.value|default:'' }}"
           id="{{ widget.attrs.id }}_input">
</div>
```

*   `skill-tree-widget`: The main container for the widget.
*   `skill-search`: Contains the search input (`skill-search-input`).
*   `skill-categories`: This div will hold the dynamically generated skill categories and their associated skills.
*   **Hidden Input**: Stores the selected skills and proficiency data as a JSON string. The `name` attribute will be "skills" to match the form field.

**Data Flow to the Template:**

1.  **View:** When the `JobPostingForm` is rendered, the view will need to pass the skill tree data to the template context. This can be done by querying all the skills and structuring them appropriately:

    ```python
    from django.core.serializers.json import DjangoJSONEncoder

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Simple structure suitable for JavaScript
        def build_category_tree(skills):
            categories = {}
            for skill in skills:
                path_parts = skill.path.split(":")
                current_level = categories

                for i, part in enumerate(path_parts):
                    if part not in current_level:
                        current_level[part] = {
                            "label": skill.label if i == len(path_parts) - 1 else "",
                            "icon": skill.icon if i == len(path_parts) - 1 else "",
                            "skills": [] if i == len(path_parts) - 1 else {},
                            "id": skill.pk if i == len(path_parts) - 1 else None
                        }

                    if i == len(path_parts) - 1:
                        current_level[part]["skills"].append({
                            "id": skill.pk,
                            "label": skill.label,
                            "icon": skill.icon,
                            "path": skill.path
                        })
                    else:
                        current_level = current_level[part]["skills" if i == len(path_parts) - 2 else "children"]

            return categories

        all_skills = SkillTreeModel.objects.all()
        categories = build_category_tree(all_skills)

        context['categories_json'] = json.dumps(categories, cls=DjangoJSONEncoder)
        return context

    ```

### 3. `skill-tree-widget.js` (JavaScript)

This script handles the dynamic rendering of the skill tree and user interactions.

```javascript
class SkillTreeWidget {
    constructor(element) {
        this.container = element;
        this.input = element.querySelector(`#${element.id}_input`);
        this.categoriesContainer = element.querySelector('.skill-categories');
        this.search = element.querySelector('.skill-search-input');
        this.selectedSkills = new Map(); // {skillId: proficiencyLevel}
        this.categoriesData = JSON.parse(element.querySelector('.skill-categories').getAttribute('data-categories'));
        this.init();
    }

    init() {
        this.renderSkillTree();
        this.setupEventListeners();
    }

    renderSkillTree() {
        this.categoriesContainer.innerHTML = ''; // Clear existing content

        const ul = document.createElement('ul');
        this.categoriesContainer.appendChild(ul);
        this.buildCategoryTree(ul, this.categoriesData);
    }

    buildCategoryTree(parent, categories) {
        for (const categoryKey in categories) {
            const category = categories[categoryKey];
            const li = document.createElement('li');
            
            if (category.label) {
                const categoryDiv = document.createElement('div');
                categoryDiv.className = 'skill-category';

                const header = document.createElement('div');
                header.className = 'category-header';

                if (category.icon) {
                    const icon = document.createElement('i');
                    icon.className = category.icon;
                    header.appendChild(icon);
                }

                const label = document.createElement('span');
                label.textContent = category.label;
                header.appendChild(label);

                categoryDiv.appendChild(header);

                const items = document.createElement('div');
                items.className = 'category-items';

                category.skills.forEach(skill => {
                    const skillItem = document.createElement('div');
                    skillItem.className = 'skill-item';
                    skillItem.setAttribute('data-skill-id', skill.id);
                    skillItem.setAttribute('data-path', skill.path);

                    if (skill.icon) {
                        const skillIcon = document.createElement('i');
                        skillIcon.className = skill.icon;
                        skillItem.appendChild(skillIcon);
                    }

                    const skillLabel = document.createElement('span');
                    skillLabel.textContent = skill.label;
                    skillItem.appendChild(skillLabel);

                    items.appendChild(skillItem);
                });

                categoryDiv.appendChild(items);
                li.appendChild(categoryDiv);
            }

            if (category.children) {
                const subUl = document.createElement('ul');
                this.buildCategoryTree(subUl, category.children);
                li.appendChild(subUl);
            }
            
            parent.appendChild(li);
        }
    }

    setupEventListeners() {
        this.categoriesContainer.addEventListener('click', (event) => {
            const skillItem = event.target.closest('.skill-item');
            if (skillItem) {
                const skillId = parseInt(skillItem.getAttribute('data-skill-id'));
                this.onSkillSelect(skillId);
            }
        });

        this.search.addEventListener('input', () => {
            this.filterSkills(this.search.value.toLowerCase());
        });
    }

    onSkillSelect(skillId) {
        // Create a dialog or dropdown for proficiency selection
        // ... (Implementation for proficiency selection) ...

        // For simplicity, let's assume a basic prompt for now:
        const proficiency = prompt("Enter proficiency level (required, preferred, bonus):", "required");
        if (proficiency && ['required', 'preferred', 'bonus'].includes(proficiency.toLowerCase())) {
            this.selectedSkills.set(skillId, proficiency);
            this.updateFormData();
        } else if (proficiency !== null) {
            alert("Invalid proficiency level. Please enter 'required', 'preferred', or 'bonus'.");
        }
    }

    updateFormData() {
        const formData = Array.from(this.selectedSkills.entries()).map(([skillId, proficiency]) => ({
            skill: skillId,
            proficiency: proficiency
        }));
        this.input.value = JSON.stringify(formData);
    }

    filterSkills(searchTerm) {
        const allSkillItems = this.categoriesContainer.querySelectorAll('.skill-item');
        allSkillItems.forEach(item => {
            const label = item.querySelector('span').textContent.toLowerCase();
            if (label.includes(searchTerm)) {
                item.style.display = ''; // Show
            } else {
                item.style.display = 'none'; // Hide
            }
        });
    }
}

// Initialize the widget
document.addEventListener('DOMContentLoaded', () => {
    const skillTreeWidgets = document.querySelectorAll('.skill-tree-widget');
    skillTreeWidgets.forEach(widget => new SkillTreeWidget(widget));
});
```

*   **`constructor`**:
    *   Gets references to the main container, hidden input, categories container, and search input.
    *   Initializes `selectedSkills` to an empty map.
    *   Calls `init()` to set up the widget.
*   **`init`**:
    *   Calls `renderSkillTree` to render the initial skill tree.
    *   Calls `setupEventListeners` to add event listeners for user interactions.
*   **`renderSkillTree`**:
    *   Clears any existing content in `categoriesContainer`.
    *   Creates a `<ul>` element and appends it to `categoriesContainer`.
    *   Calls `buildCategoryTree` to recursively build the tree structure.
*   **`buildCategoryTree`**:
    *   Recursively processes each category and its subcategories.
    *   Creates `<li>` elements for each category and skill.
    *   Adds appropriate CSS classes and data attributes (`data-skill-id`, `data-path`).
    *   Handles cases where a category might not have a label (intermediate nodes).
*   **`setupEventListeners`**:
    *   Adds a 'click' event listener to `categoriesContainer` to handle skill selection.
    *   Adds an 'input' event listener to the search input to handle filtering.
*   **`onSkillSelect`**:
    *   Currently uses a basic `prompt` to get the proficiency level (this should be replaced with a more user-friendly UI element).
    *   Validates the proficiency level.
    *   Updates `selectedSkills` and calls `updateFormData`.
*   **`updateFormData`**:
    *   Converts `selectedSkills` to the required JSON format.
    *   Updates the hidden input's value.
*   **`filterSkills`**:
    *   Filters skill items based on the search term.
    *   Shows/hides skill items based on whether their label matches the search term.

### 4. Form Logic (`clean_skills` and `save`)

```python
class JobPostingForm(forms.ModelForm):
    # ... (Widget definition) ...

    def clean_skills(self):
        skills_data = self.cleaned_data.get('skills')
        if not skills_data:
            return []  # No skills selected

        try:
            skills = json.loads(skills_data)
            validated_skills = []

            for item in skills:
                skill_id = item.get