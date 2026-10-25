from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AccountTests(TestCase):
    def test_register_creates_user_with_hashed_password(self):
        response = self.client.post(reverse("register"), {
            "username": "riya",
            "first_name": "Riya",
            "email": "riya@example.com",
            "password1": "a-Strong-pass-123",
            "password2": "a-Strong-pass-123",
        })
        self.assertRedirects(response, reverse("dashboard"))
        user = User.objects.get(username="riya")
        self.assertEqual(user.first_name, "Riya")
        self.assertNotEqual(user.password, "a-Strong-pass-123")  # stored as a hash
        self.assertTrue(user.check_password("a-Strong-pass-123"))

    def test_register_shows_errors_for_mismatched_passwords(self):
        response = self.client.post(reverse("register"), {
            "username": "riya",
            "first_name": "Riya",
            "email": "riya@example.com",
            "password1": "a-Strong-pass-123",
            "password2": "something-else-456",
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errorlist")
        self.assertFalse(User.objects.filter(username="riya").exists())

    def test_login_and_logout(self):
        User.objects.create_user("sam", "sam@example.com", "a-Strong-pass-123")
        response = self.client.post(reverse("login"), {
            "username": "sam",
            "password": "a-Strong-pass-123",
        })
        self.assertRedirects(response, reverse("dashboard"))

        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
        # After logging out, private pages send us to the login page.
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_wrong_password_is_rejected(self):
        User.objects.create_user("sam", "sam@example.com", "a-Strong-pass-123")
        response = self.client.post(reverse("login"), {"username": "sam", "password": "wrong"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "errorlist")

    def test_delete_account_needs_correct_password(self):
        User.objects.create_user("sam", "sam@example.com", "a-Strong-pass-123")
        self.client.login(username="sam", password="a-Strong-pass-123")

        response = self.client.post(reverse("delete_account"), {"password": "wrong"})
        self.assertContains(response, "The password is not correct.")
        self.assertTrue(User.objects.filter(username="sam").exists())

        response = self.client.post(reverse("delete_account"), {"password": "a-Strong-pass-123"})
        self.assertRedirects(response, reverse("login"))
        self.assertFalse(User.objects.filter(username="sam").exists())

    def test_private_pages_need_login(self):
        for name in ["dashboard", "item_list", "category_list", "reminder_list",
                     "notification_list", "record_list", "impact_summary", "account"]:
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 302, name)
            self.assertIn(reverse("login"), response.url)
