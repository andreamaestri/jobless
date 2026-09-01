from django import forms
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import gettext_lazy as _
import json
from .models import (
    JobPosting,
    SkillTreeModel,
    JobSkill,
    UserProfile,
    ObligationPlan,
    Application,
)


class SkillTreeWidget(forms.SelectMultiple):
    template_name = 'jobs/widgets/skill_tree_widget.html'

    class Media:
        pass

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
                            ),
                            "proficiency_levels": dict(JobSkill.PROFICIENCY_LEVELS)
                        }

                    if i == len(path_parts) - 1:
                        current_level[part]["skills"].append(
                            {
                                "id": skill.pk,
                                "label": skill.label,
                                "icon": skill.get_icon(),
                                "path": skill.path,
                                "proficiency_levels": dict(JobSkill.PROFICIENCY_LEVELS)
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
        context['widget']['proficiency_levels'] = dict(JobSkill.PROFICIENCY_LEVELS)
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
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input w-full'}),
            'company': forms.TextInput(attrs={'class': 'input w-full'}),
            'location': forms.TextInput(attrs={'class': 'input w-full'}),
            'salary_range': forms.TextInput(attrs={'class': 'input w-full'}),
            'url': forms.URLInput(attrs={'class': 'input w-full'}),
            'description': forms.Textarea(attrs={'class': 'textarea w-full'}),
            'status': forms.Select(attrs={'class': 'select w-full'}),
        }
        labels = {
            'title': _('Job title'),
            'company': _('Company'),
            'location': _('Location'),
            'salary_range': _('Salary range'),
            'url': _('Job posting URL'),
            'description': _('Job description'),
            'skills': _('Skills'),
            'status': _('Application status'),
        }

    def clean_skills(self):
        skills_data = self.cleaned_data.get('skills')
        if not skills_data:
            return []

        try:
            skills = json.loads(skills_data)
            if not isinstance(skills, list):
                raise forms.ValidationError('Skills data must be a list')

            validated_skills = []
            errors = []

            for index, item in enumerate(skills):
                try:
                    if not isinstance(item, dict):
                        raise forms.ValidationError(f'Invalid skill data format at index {index}')

                    skill_id = item.get('skill')
                    proficiency = item.get('proficiency')

                    if not skill_id:
                        raise forms.ValidationError(f'Missing skill ID at index {index}')
                    if not proficiency:
                        raise forms.ValidationError(f'Missing proficiency at index {index}')

                    proficiency_levels = dict(JobSkill.PROFICIENCY_LEVELS)
                    if proficiency not in proficiency_levels:
                        raise forms.ValidationError(
                            f'Invalid proficiency level "{proficiency}" at index {index}. '
                            f'Valid levels are: {", ".join(proficiency_levels.keys())}'
                        )

                    try:
                        skill = SkillTreeModel.objects.get(pk=skill_id)
                        validated_skills.append({
                            'skill': skill,
                            'proficiency': proficiency
                        })
                    except SkillTreeModel.DoesNotExist:
                        raise forms.ValidationError(f'Skill with ID {skill_id} does not exist')

                except forms.ValidationError as e:
                    errors.extend(e.messages)

            if errors:
                raise forms.ValidationError(errors)

            return validated_skills

        except json.JSONDecodeError:
            raise forms.ValidationError('Invalid JSON data format')
        except Exception as e:
            raise forms.ValidationError(f'Error processing skills: {str(e)}')

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


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            'applied_on', 'employer_name', 'job_title', 'channel', 'result',
            'employer_address', 'employer_phone', 'employer_email',
            'contact_person', 'source', 'source_ref', 'result_date',
            'result_note', 'effort_type', 'related_to_vermittlungsvorschlag',
            'costs_cents',
        ]
        widgets = {
            'applied_on': forms.DateInput(
                attrs={'type': 'date', 'class': 'input w-full'},
                format='%Y-%m-%d',
            ),
            'employer_name': forms.TextInput(attrs={'class': 'input w-full'}),
            'job_title': forms.TextInput(attrs={'class': 'input w-full'}),
            'channel': forms.Select(attrs={'class': 'select w-full'}),
            'result': forms.Select(attrs={'class': 'select w-full'}),
            'employer_address': forms.TextInput(attrs={'class': 'input w-full'}),
            'employer_phone': forms.TextInput(attrs={'class': 'input w-full'}),
            'employer_email': forms.EmailInput(attrs={'class': 'input w-full'}),
            'contact_person': forms.TextInput(attrs={'class': 'input w-full'}),
            'source': forms.Select(attrs={'class': 'select w-full'}),
            'source_ref': forms.TextInput(attrs={'class': 'input w-full'}),
            'result_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'input w-full'},
                format='%Y-%m-%d',
            ),
            'result_note': forms.TextInput(attrs={'class': 'input w-full'}),
            'effort_type': forms.Select(attrs={'class': 'select w-full'}),
            'related_to_vermittlungsvorschlag': forms.CheckboxInput(
                attrs={'class': 'toggle toggle-primary'}
            ),
            'costs_cents': forms.NumberInput(attrs={'class': 'input w-full'}),
        }
        labels = {
            'applied_on': _('Applied on'),
            'employer_name': _('Employer'),
            'job_title': _('Job title'),
            'channel': _('How applied'),
            'result': _('Status'),
            'employer_address': _('Employer address'),
            'employer_phone': _('Employer phone'),
            'employer_email': _('Employer e-mail'),
            'contact_person': _('Contact person'),
            'source': _('Source'),
            'source_ref': _('Source reference (URL)'),
            'result_date': _('Result date'),
            'result_note': _('Result note'),
            'effort_type': _('Effort type'),
            'related_to_vermittlungsvorschlag': _('Related to placement proposal'),
            'costs_cents': _('Costs (cents)'),
        }


class ObligationPlanForm(forms.ModelForm):
    class Meta:
        model = ObligationPlan
        fields = [
            'title', 'caseworker', 'valid_from', 'valid_to', 'required_count',
            'period', 'due_rule', 'due_rule_notes', 'accepted_channels',
            'proof_form', 'notes', 'counts_interviews_as_effort',
            'counts_measures_as_effort', 'counts_jobboard_search_as_effort',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input w-full'}),
            'caseworker': forms.Select(attrs={'class': 'select w-full'}),
            'valid_from': forms.DateInput(
                attrs={'type': 'date', 'class': 'input w-full'},
                format='%Y-%m-%d',
            ),
            'valid_to': forms.DateInput(
                attrs={'type': 'date', 'class': 'input w-full'},
                format='%Y-%m-%d',
            ),
            'required_count': forms.NumberInput(attrs={'class': 'input w-full'}),
            'period': forms.Select(attrs={'class': 'select w-full'}),
            'due_rule': forms.Select(attrs={'class': 'select w-full'}),
            'due_rule_notes': forms.TextInput(attrs={'class': 'input w-full'}),
            'accepted_channels': forms.Textarea(attrs={'class': 'textarea w-full', 'rows': 3}),
            'proof_form': forms.Select(attrs={'class': 'select w-full'}),
            'notes': forms.Textarea(attrs={'class': 'textarea w-full', 'rows': 3}),
            'counts_interviews_as_effort': forms.CheckboxInput(attrs={'class': 'toggle toggle-primary'}),
            'counts_measures_as_effort': forms.CheckboxInput(attrs={'class': 'toggle toggle-primary'}),
            'counts_jobboard_search_as_effort': forms.CheckboxInput(attrs={'class': 'toggle toggle-primary'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'toggle toggle-primary'}),
        }
        labels = {
            'title': _('Title'),
            'caseworker': _('Caseworker'),
            'valid_from': _('Valid from'),
            'valid_to': _('Valid to'),
            'required_count': _('Required count'),
            'period': _('Period'),
            'due_rule': _('Due rule'),
            'due_rule_notes': _('Due rule notes'),
            'accepted_channels': _('Accepted channels'),
            'proof_form': _('Proof form'),
            'notes': _('Notes (verbatim from your plan)'),
            'counts_interviews_as_effort': _('Interviews count as effort'),
            'counts_measures_as_effort': _('Measures count as effort'),
            'counts_jobboard_search_as_effort': _('Job board search counts as effort'),
            'is_active': _('Active'),
        }

    def clean_accepted_channels(self):
        value = self.cleaned_data.get('accepted_channels')
        if isinstance(value, str):
            value = [item.strip() for item in value.split(',') if item.strip()]
        return value


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'full_name', 'kundennummer', 'bg_nummer', 'address', 'email',
            'phone', 'regime', 'office_name', 'preferred_locale',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'input w-full'}),
            'kundennummer': forms.TextInput(attrs={'class': 'input w-full'}),
            'bg_nummer': forms.TextInput(attrs={'class': 'input w-full'}),
            'address': forms.Textarea(attrs={'class': 'textarea w-full', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'input w-full'}),
            'phone': forms.TextInput(attrs={'class': 'input w-full'}),
            'regime': forms.Select(attrs={'class': 'select w-full'}),
            'office_name': forms.TextInput(attrs={'class': 'input w-full'}),
            'preferred_locale': forms.TextInput(attrs={'class': 'input w-full'}),
        }
        labels = {
            'full_name': _('Full name'),
            'kundennummer': _('Kundennummer'),
            'bg_nummer': _('BG-Nummer'),
            'address': _('Address'),
            'email': _('E-mail'),
            'phone': _('Phone'),
            'regime': _('Regime'),
            'office_name': _('Office'),
            'preferred_locale': _('Preferred locale'),
        }
