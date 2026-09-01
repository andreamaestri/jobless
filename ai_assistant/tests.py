from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SecureClientMixin:
    """Production forces SECURE_SSL_REDIRECT; test requests must use https."""

    def get(self, *args, **kwargs):
        kwargs.setdefault("secure", True)
        return self.client.get(*args, **kwargs)


class AssistantViewTests(SecureClientMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username="tester", password="pw12345")

    def test_assistant_requires_login(self):
        response = self.get(reverse("ai_assistant:assistant"))
        self.assertEqual(response.status_code, 302)

    def test_assistant_renders_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.get(reverse("ai_assistant:assistant"))
        self.assertEqual(response.status_code, 200)
