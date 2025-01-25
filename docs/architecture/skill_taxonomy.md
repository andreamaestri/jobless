# Skill Taxonomy System Design

## Overview

This document outlines the improved skill taxonomy system using django-tagulous tag trees, combining hierarchical organization with rich metadata support.

## Core Components

### 1. Tag Tree Model

```python
from tagulous.models import TagTreeModel

class SkillTreeModel(TagTreeModel):
    # Metadata fields
    icon = models.CharField(max_length=100, blank=True)
    icon_dark = models.CharField(max_length=100, blank=True)
    
    class TagMeta:
        force_lowercase = True
        space_delimiter = False
        max_count = 10
        tree = True  # Enable tag tree functionality
        
        # Initial data will be loaded from fixtures
        initial = None
        
    def get_icon(self):
        """Get icon based on skill name hierarchy"""
        if not self.icon:
            # Try exact match first
            icon_match = SKILL_ICONS.get(self.label.lower())
            if icon_match:
                self.icon = icon_match
                self.save()
            # Try parent category if no match
            elif self.parent:
                return self.parent.get_icon()
        return self.icon or 'heroicons:academic-cap'
```

### 2. Job-Skill Relationship

```python
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
    
    class Meta:
        unique_together = ['job', 'skill']
```

### 3. Skill Fixtures

```yaml
# skills.yaml
- model: jobs.skilltreemodel
  fields:
    name: "Programming"
    path: "programming"
    label: "Programming"
    level: 1
    
- model: jobs.skilltreemodel
  fields:
    name: "Programming/Languages"
    path: "programming/languages"
    label: "Languages"
    level: 2
    
- model: jobs.skilltreemodel
  fields:
    name: "Programming/Languages/Python"
    path: "programming/languages/python"
    label: "Python"
    level: 3
    icon: "skill-icons:python"
```

## Implementation Strategy

### 1. Migration Plan

1. Create initial migration:
```python
operations = [
    migrations.CreateModel(
        name='SkillTreeModel',
        fields=[
            ('id', models.AutoField(auto_created=True, primary_key=True)),
            ('name', models.CharField(max_length=255, unique=True)),
            ('path', models.TextField(unique=True)),
            ('label', models.CharField(max_length=255)),
            ('level', models.IntegerField(default=1)),
            ('parent', models.ForeignKey('self', null=True, blank=True)),
            ('icon', models.CharField(max_length=100, blank=True)),
            ('icon_dark', models.CharField(max_length=100, blank=True)),
        ],
        bases=(tagulous.models.models.BaseTagTreeModel, models.Model),
    ),
]
```

2. Data migration for existing skills:
```python
def migrate_skills(apps, schema_editor):
    SkillTreeModel = apps.get_model('jobs', 'SkillTreeModel')
    JobPosting = apps.get_model('jobs', 'JobPosting')
    
    # Create category structure
    categories = {
        'Programming': ['Python', 'JavaScript', 'Java'],
        'Frontend': ['React', 'Vue', 'Angular'],
        'Backend': ['Django', 'Node.js', 'Spring'],
        'DevOps': ['Docker', 'Kubernetes', 'AWS']
    }
    
    for category, skills in categories.items():
        cat_obj = SkillTreeModel.objects.create(name=category)
        for skill in skills:
            SkillTreeModel.objects.create(
                name=f"{category}/{skill}",
                parent=cat_obj
            )
```

### 2. Query Patterns

```python
# Get all programming languages
programming_skills = SkillTreeModel.objects.filter(
    path__startswith='programming/languages/'
)

# Get jobs requiring Python with related skills
python_jobs = JobPosting.objects.filter(
    jobskill__skill__path__endswith='/python',
    jobskill__proficiency='required'
)

# Get skill hierarchy for a job
job_skills = job.skills.as_nested_list()
```

### 3. Frontend Integration

```html
<!-- Skill selector with hierarchical display -->
<div class="skill-tree">
  {% for category, skills in skill_tree %}
    <div class="skill-category">
      <h3>{{ category.label }}</h3>
      <div class="skill-list">
        {% for skill in skills %}
          <div class="skill-item">
            <i class="{{ skill.get_icon }}"></i>
            {{ skill.label }}
          </div>
        {% endfor %}
      </div>
    </div>
  {% endfor %}
</div>
```

## Benefits

1. **Improved Organization**
   - Natural hierarchy for skills
   - Category-based navigation
   - Efficient querying of related skills

2. **Better Maintainability**
   - Centralized skill definitions
   - Automated parent/child relationships
   - Simplified icon management

3. **Enhanced User Experience**
   - Hierarchical skill selection
   - Intuitive skill categorization
   - Clear proficiency levels

4. **Performance Optimizations**
   - Efficient tree queries
   - Reduced database joins
   - Better caching opportunities

## Future Enhancements

1. **Skill Analytics**
   - Track skill popularity by level
   - Analyze skill relationships
   - Identify trending skills

2. **Advanced Querying**
   - Skills by experience level
   - Related skill suggestions
   - Job compatibility scoring

3. **UI Improvements**
   - Dynamic skill tree visualization
   - Interactive skill selection
   - Skill relationship graph