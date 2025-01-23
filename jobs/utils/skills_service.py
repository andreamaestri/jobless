from .skill_icons import DARK_VARIANTS, ICON_NAME_MAPPING, SKILL_ICONS
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

class SkillsService:
    @staticmethod
    def get_skill_groups():
        """Group skills by first letter with proper icon handling"""
        skill_groups = {}
        
        for icon, name in SKILL_ICONS:
            first_letter = name[0].upper()
            if first_letter not in skill_groups:
                skill_groups[first_letter] = []
                
            # Get the formatted icon
            formatted_icon = icon
            if icon in DARK_VARIANTS:
                dark_icon = DARK_VARIANTS[icon]
            else:
                # Check if the icon exists in the mapping
                mapped_icon = ICON_NAME_MAPPING.get(name, icon)
                dark_icon = DARK_VARIANTS.get(mapped_icon, mapped_icon)
                
            skill_groups[first_letter].append({
                'name': name,
                'icon': formatted_icon,
                'icon_dark': dark_icon
            })

        # Convert to sorted list of groups
        return [
            {
                'letter': letter,
                'skills': sorted(skills, key=lambda x: x['name'])
            }
            for letter, skills in sorted(skill_groups.items())
        ]

    @staticmethod
    def get_autocomplete_results(query='', all_skills=False):
        """Get autocomplete results for skills"""
        skills_data = list(SKILL_ICONS)  # Convert to list to ensure it's mutable
        
        # Filter if there's a query and not requesting all
        if query and not all_skills:
            skills_data = [
                (icon, name) for icon, name in skills_data 
                if query.lower() in name.lower()
            ]
        
        # Group skills by first letter with proper icon handling
        grouped_skills = {}
        for icon, name in skills_data:
            first_letter = name[0].upper()
            if first_letter not in grouped_skills:
                grouped_skills[first_letter] = []
            
            # Ensure proper icon formatting
            icon_name = icon.replace('skill-icons:', '')
            formatted_icon = f"skill-icons:{icon_name}"
            dark_icon = DARK_VARIANTS.get(formatted_icon, formatted_icon)
            
            grouped_skills[first_letter].append({
                'name': name,
                'icon': formatted_icon,
                'icon_dark': dark_icon
            })
        
        # Convert to sorted list of groups
        return [
            {
                'letter': letter,
                'skills': sorted(grouped_skills[letter], key=lambda x: x['name'].upper())
            }
            for letter in sorted(grouped_skills.keys())
        ]
