from django.db import migrations

def set_parent_relationships(apps, schema_editor):
    SkillTreeModel = apps.get_model('jobs', 'SkillTreeModel')
    
    # Get all skills
    skills = SkillTreeModel.objects.all()
    
    # For each skill, find and set its parent based on path
    for skill in skills:
        if '/' in skill.path:
            parent_path = skill.path.rsplit('/', 1)[0]
            try:
                parent = SkillTreeModel.objects.get(path=parent_path)
                skill.parent = parent
                skill.save()
            except SkillTreeModel.DoesNotExist:
                continue

def reverse_parent_relationships(apps, schema_editor):
    SkillTreeModel = apps.get_model('jobs', 'SkillTreeModel')
    SkillTreeModel.objects.all().update(parent=None)

class Migration(migrations.Migration):
    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            set_parent_relationships,
            reverse_parent_relationships
        )
    ]
