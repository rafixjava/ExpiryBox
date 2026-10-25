from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from items.models import Category, Item

from .models import Notification, Reminder


class ReminderAndNotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("riya", "riya@example.com", "a-Strong-pass-123")
        self.other = User.objects.create_user("sam", "sam@example.com", "a-Strong-pass-123")
        self.today = timezone.localdate()
        category = Category.objects.first()
        self.item = Item.objects.create(
            user=self.user, category=category, item_name="Milk",
            expiry_date=self.today + timedelta(days=3),
        )
        self.others_item = Item.objects.create(
            user=self.other, category=category, item_name="Bread",
            expiry_date=self.today + timedelta(days=3),
        )
        self.client.login(username="riya", password="a-Strong-pass-123")

    def test_add_edit_delete_reminder(self):
        response = self.client.post(reverse("reminder_add"), {
            "item": self.item.pk,
            "reminder_date": self.today + timedelta(days=2),
            "reminder_type": "DAY_BEFORE",
        })
        self.assertRedirects(response, reverse("reminder_list"))
        reminder = Reminder.objects.get(item=self.item)
        self.assertFalse(reminder.is_sent)

        self.client.post(reverse("reminder_edit", args=[reminder.pk]), {
            "item": self.item.pk,
            "reminder_date": self.today + timedelta(days=1),
            "reminder_type": "CUSTOM",
        })
        reminder.refresh_from_db()
        self.assertEqual(reminder.reminder_type, "CUSTOM")

        self.client.post(reverse("reminder_delete", args=[reminder.pk]))
        self.assertFalse(Reminder.objects.filter(pk=reminder.pk).exists())

    def test_cannot_add_reminder_for_another_users_item(self):
        response = self.client.post(reverse("reminder_add"), {
            "item": self.others_item.pk,
            "reminder_date": self.today,
            "reminder_type": "CUSTOM",
        })
        self.assertEqual(response.status_code, 200)  # form shown again with an error
        self.assertContains(response, "errorlist")
        self.assertEqual(Reminder.objects.count(), 0)

    def test_due_reminder_creates_exactly_one_notification(self):
        Reminder.objects.create(item=self.item, reminder_date=self.today)
        future = Reminder.objects.create(item=self.item, reminder_date=self.today + timedelta(days=2))

        # Opening the pages several times must not create duplicates.
        self.client.get(reverse("dashboard"))
        self.client.get(reverse("notification_list"))
        self.client.get(reverse("dashboard"))

        notifications = Notification.objects.filter(user=self.user)
        self.assertEqual(notifications.count(), 1)
        self.assertEqual(notifications[0].item, self.item)
        self.assertIn("expires in 3 day(s)", notifications[0].message)
        future.refresh_from_db()
        self.assertFalse(future.is_sent)  # not due yet

    def test_mark_read_and_delete_notification(self):
        notification = Notification.objects.create(user=self.user, item=self.item, message="Hello")
        self.client.post(reverse("notification_mark_read", args=[notification.pk]))
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

        self.client.post(reverse("notification_delete", args=[notification.pk]))
        self.assertFalse(Notification.objects.filter(pk=notification.pk).exists())

    def test_other_users_records_are_protected(self):
        others_reminder = Reminder.objects.create(item=self.others_item, reminder_date=self.today)
        others_notification = Notification.objects.create(user=self.other, message="Private")

        self.assertEqual(self.client.get(reverse("reminder_edit", args=[others_reminder.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("notification_delete", args=[others_notification.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("notification_list")), "Private")
        # Visiting our pages must not "send" another user's reminder.
        others_reminder.refresh_from_db()
        self.assertFalse(others_reminder.is_sent)
