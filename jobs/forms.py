from django import forms
from django.core.serializers.json import DjangoJSONEncoder
import json
from .models import JobPosting, SkillTreeModel, JobSkill


class SkillTreeWidget(forms.SelectMultiple):
    template_name = 'jobs/widgets/skill_tree_widget.html'

    class Media:
        css = {
            'all': ['css/skill-tree.css']
        }
        js = ['js/skill-tree-widget.js']

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)

        def build_category_tree(skills):
            categories = {}
            for skill in skills:
                path_parts = skill.path.split(":")
                current_level = categories

                for i, part in enumerate(path_parts):
                    if part not in current_level:
                        current_level[part] = {
                            "label": (
                                skill.label if i == len(path_parts) - 1 else ""
                            ),
                            "icon": (
                                skill.icon if i == len(path_parts) - 1 else ""
                            ),
                            "skills": (
                                [] if i == len(path_parts) - 1 else {}
                            ),
                            "id": (
                                skill.pk if i == len(path_parts) - 1 else None
                            )
                        }

                    if i == len(path_parts) - 1:
                        current_level[part]["skills"].append(
                            {
                                "id": skill.pk,
                                "label": skill.label,
                                "icon": skill.get_icon(),
                                "path": skill.path
                            }
                        )
                    else:
                        is_second_to_last = i == len(path_parts) - 2
                        key = "skills" if is_second_to_last else "children"
                        current_level = current_level[part][key]

            return categories

        all_skills = SkillTreeModel.objects.all()
        tree_data = build_category_tree(all_skills)
        context['widget']['categories_json'] = json.dumps(
            tree_data, cls=DjangoJSONEncoder
        )
        return context


class JobPostingForm(forms.ModelForm):
    skills = forms.CharField(
        widget=SkillTreeWidget(attrs={'class': 'skill-tree-select'}),
        required=False  # Skills are optional
    )

    class Meta:
        model = JobPosting
        fields = [
            'title', 'company', 'location', 'salary_range',
            'url', 'description', 'skills', 'status'
        ]

    def clean_skills(self):
        skills_data = self.cleaned_data.get('skills')
        if not skills_data:
            return []

        try:
            skills = json.loads(skills_data)
            validated_skills = []

            for item in skills:
                skill_id = item.get('skill')
                proficiency = item.get('proficiency')

                if not skill_id or not proficiency:
                    raise forms.ValidationError('Invalid skill data format')

                proficiency_levels = dict(JobSkill.PROFICIENCY_LEVELS)
                if proficiency not in proficiency_levels:
                    raise forms.ValidationError(
                        f'Invalid proficiency level: {proficiency}'
                    )

                try:
                    skill = SkillTreeModel.objects.get(pk=skill_id)
                    validated_skills.append({
                        'skill': skill,
                        'proficiency': proficiency
                    })
                except SkillTreeModel.DoesNotExist:
                    raise forms.ValidationError(
                        f'Skill with ID {skill_id} does not exist'
                    )

            return validated_skills
        except json.JSONDecodeError:
            raise forms.ValidationError('Invalid JSON data')
        except Exception as e:
            raise forms.ValidationError(
                f'Error processing skills: {str(e)}'
            )

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if commit:
            instance.save()
            
            # Clear existing skills
            instance.job_skills.all().delete()
            
            # Add new skills
            validated_skills = self.cleaned_data.get('skills', [])
            for skill_data in validated_skills:
                JobSkill.objects.create(
                    job=instance,
                    skill=skill_data['skill'],
                    proficiency=skill_data['proficiency']
                )

        return instance
