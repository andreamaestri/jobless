# Skill Components Technical Specification

## 1. Proficiency Selection Component

### Model Integration
```python
# jobs/models.py
class JobSkill(models.Model):
    PROFICIENCY_LEVELS = [
        ('required', 'Required'),
        ('preferred', 'Preferred'),
        ('bonus', 'Nice to Have')
    ]
    
    job = models.ForeignKey('JobPosting', on_delete=models.CASCADE)
    skill = models.ForeignKey(SkillTreeModel, on_delete=models.CASCADE)
    proficiency = models.CharField(
        max_length=20,
        choices=PROFICIENCY_LEVELS,
        default='required'
    )
```

### Alpine.js State Management
```javascript
// static/js/skill-proficiency.js
document.addEventListener('alpine:init', () => {
    Alpine.data('skillProficiency', () => ({
        skills: {},  // {skillId: {name, proficiency}}
        
        init() {
            // Load existing skills and proficiencies
            this.skills = JSON.parse(this.$el.dataset.skills || '{}')
        },
        
        updateProficiency(skillId, level) {
            this.skills[skillId] = {
                ...this.skills[skillId],
                proficiency: level
            }
            this.$dispatch('skill-updated', {
                skillId,
                proficiency: level
            })
        }
    }))
})
```

### Component Template
```html
<!-- templates/jobs/components/skill_proficiency.html -->
<div x-data="skillProficiency" 
     x-init="init()"
     :data-skills="JSON.stringify(initialSkills)">
    
    <template x-for="(skill, id) in skills" :key="id">
        <div class="skill-item">
            <div class="skill-info">
                <i :class="skill.icon"></i>
                <span x-text="skill.name"></span>
            </div>
            
            <div class="proficiency-selector">
                <template x-for="level in ['required', 'preferred', 'bonus']">
                    <button 
                        @click="updateProficiency(id, level)"
                        :class="{
                            'active': skill.proficiency === level
                        }"
                        x-text="level">
                    </button>
                </template>
            </div>
        </div>
    </template>
</div>
```

## 2. Hierarchical Skill Navigator

### Tree View Component
```javascript
// static/js/skill-tree-navigator.js
Alpine.data('skillTree', () => ({
    categories: [],
    expandedNodes: new Set(),
    selectedPath: null,
    
    async init() {
        // Fetch skill tree structure
        const response = await fetch('/api/skills/tree/')
        this.categories = await response.json()
    },
    
    toggleNode(path) {
        if (this.expandedNodes.has(path)) {
            this.expandedNodes.delete(path)
        } else {
            this.expandedNodes.add(path)
        }
    },
    
    isExpanded(path) {
        return this.expandedNodes.has(path)
    },
    
    selectSkill(path) {
        this.selectedPath = path
        this.$dispatch('skill-selected', { path })
    }
}))
```

### Tree View Template
```html
<!-- templates/jobs/components/skill_tree.html -->
<div x-data="skillTree"
     x-init="init()"
     class="skill-tree-navigator">
     
    <template x-for="category in categories" :key="category.path">
        <div class="category-node">
            <div class="node-header"
                 @click="toggleNode(category.path)">
                <i :class="isExpanded(category.path) ? 'expanded-icon' : 'collapsed-icon'"></i>
                <span x-text="category.label"></span>
            </div>
            
            <div x-show="isExpanded(category.path)"
                 class="node-children">
                <template x-for="skill in category.children" :key="skill.path">
                    <div class="skill-node"
                         :class="{ 'selected': selectedPath === skill.path }"
                         @click="selectSkill(skill.path)">
                        <i :class="skill.icon"></i>
                        <span x-text="skill.label"></span>
                    </div>
                </template>
            </div>
        </div>
    </template>
</div>
```

### API Integration

```python
# jobs/views.py
from django.http import JsonResponse

class SkillTreeView(View):
    def get(self, request):
        skills = SkillTreeModel.objects.as_nested_list()
        return JsonResponse({
            'categories': self._format_tree(skills)
        })
    
    def _format_tree(self, nodes):
        """Convert nested list to frontend-friendly format"""
        result = []
        for node, children in nodes:
            result.append({
                'path': node.path,
                'label': node.label,
                'icon': node.get_icon(),
                'children': self._format_tree(children)
            })
        return result
```

## 3. Integration Guidelines

### Form Handling
```python
# jobs/forms.py
class JobSkillForm(forms.ModelForm):
    class Meta:
        model = JobSkill
        fields = ['skill', 'proficiency']
        widgets = {
            'skill': SkillTreeWidget,  # Custom widget for tree selection
            'proficiency': forms.RadioSelect(choices=JobSkill.PROFICIENCY_LEVELS)
        }

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'skills']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['skills'] = {
                skill.id: {
                    'proficiency': skill.jobskill_set.get(job=self.instance).proficiency
                }
                for skill in self.instance.skills.all()
            }
```

### View Integration
```python
# jobs/views.py
class JobPostingCreateView(CreateView):
    model = JobPosting
    form_class = JobPostingForm
    template_name = 'jobs/job_form.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Handle skill proficiencies
        skills_data = json.loads(self.request.POST.get('skills_data', '{}'))
        for skill_id, data in skills_data.items():
            JobSkill.objects.create(
                job=self.object,
                skill_id=skill_id,
                proficiency=data['proficiency']
            )
            
        return response
```

## 4. Styling Guidelines

### Component Themes
```css
/* static/css/skill-components.css */
.skill-tree-navigator {
    @apply bg-white dark:bg-gray-800 rounded-lg shadow-sm;
}

.category-node {
    @apply border-b border-gray-200 dark:border-gray-700;
}

.node-header {
    @apply flex items-center p-3 cursor-pointer
           hover:bg-gray-50 dark:hover:bg-gray-700;
}

.skill-node {
    @apply flex items-center p-2 pl-8 cursor-pointer
           hover:bg-blue-50 dark:hover:bg-blue-900;
}

.skill-node.selected {
    @apply bg-blue-100 dark:bg-blue-800;
}

.proficiency-selector button {
    @apply px-3 py-1 rounded-full text-sm
           border border-gray-200 dark:border-gray-700;
}

.proficiency-selector button.active {
    @apply bg-blue-500 text-white border-blue-500
           dark:bg-blue-600 dark:border-blue-600;
}
```

## 5. Testing Strategy

### Unit Tests
```python
# jobs/tests/test_skills.py
class SkillTreeTests(TestCase):
    def test_proficiency_update(self):
        job = JobPosting.objects.create(...)
        skill = SkillTreeModel.objects.create(...)
        
        JobSkill.objects.create(
            job=job,
            skill=skill,
            proficiency='required'
        )
        
        # Test proficiency update
        response = self.client.post(
            reverse('jobs:update_proficiency'),
            {
                'job_id': job.id,
                'skill_id': skill.id,
                'proficiency': 'preferred'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        job_skill = JobSkill.objects.get(job=job, skill=skill)
        self.assertEqual(job_skill.proficiency, 'preferred')
```

## 6. Performance Considerations

1. **Tree Loading**
   - Implement lazy loading for deep tree structures
   - Cache common tree paths
   - Use select_related/prefetch_related for skill queries

2. **State Management**
   - Maintain local state for UI interactions
   - Batch proficiency updates
   - Debounce tree navigation events

3. **Component Optimization**
   - Use template fragments for tree nodes
   - Implement virtual scrolling for large lists
   - Cache rendered tree structures

## 7. Implementation Roadmap

1. **Phase 1: Core Components**
   - Implement SkillTreeModel changes
   - Build basic tree navigation
   - Add proficiency UI

2. **Phase 2: UI Enhancement**
   - Add animations for tree expansion
   - Implement drag-and-drop reordering
   - Add search/filter capabilities

3. **Phase 3: Advanced Features**
   - Add skill analytics
   - Implement skill suggestions
   - Add bulk editing capabilities