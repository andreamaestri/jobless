import json

from django.test import TestCase
from django.urls import reverse

from .forms import JobPostingForm
from .models import SkillTreeModel


class SkillTaxonomyTests(TestCase):
    def setUp(self):
        self.python = SkillTreeModel.objects.create(
            name="python",
            label="Python",
            icon="skill-icons:python-dark",
            description="Python programming",
            tags="technology/programming/python",
        )
        self.nursing = SkillTreeModel.objects.create(
            name="nursing",
            label="Nursing",
            description="Patient care",
            tags="healthcare/care/nursing",
        )

    def test_api_exposes_tagulous_taxonomy_metadata(self):
        response = self.client.get(reverse("jobs:api_skills"))

        self.assertEqual(response.status_code, 200)
        skills = {skill["name"]: skill for skill in response.json()["skills"]}
        self.assertEqual(
            skills["python"]["taxonomy_path"],
            "technology/programming/python",
        )
        self.assertEqual(skills["nursing"]["description"], "Patient care")
        self.assertEqual(skills["nursing"]["icon"], "heroicons:academic-cap")

    def test_form_widget_builds_categories_from_tagulous_paths(self):
        form = JobPostingForm()
        categories = json.loads(form.fields["skills"].widget.get_context(
            "skills", None, {}
        )["widget"]["categories_json"])

        self.assertIn("technology", categories)
        self.assertIn("programming", categories["technology"]["children"])
        self.assertEqual(
            categories["technology"]["children"]["programming"]["skills"][0]["path"],
            "technology/programming/python",
        )
