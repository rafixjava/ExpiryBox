import shutil
import tempfile
from datetime import timedelta
from io import BytesIO

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from .models import Category, Item

# Save test photos in a temporary folder, not in the real media/ folder.
TEMP_MEDIA = tempfile.mkdtemp()


def make_test_photo():
    """A tiny real PNG image to upload in tests."""
    buffer = BytesIO()
    Image.new("RGB", (10, 10), "green").save(buffer, "PNG")
    return SimpleUploadedFile("milk.png", buffer.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class ItemTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user("riya", "riya@example.com", "a-Strong-pass-123")
        self.other = User.objects.create_user("sam", "sam@example.com", "a-Strong-pass-123")
        self.category = Category.objects.get(category_name="Dairy & eggs")  # from the data migration
        self.client.login(username="riya", password="a-Strong-pass-123")
        self.today = timezone.localdate()

    def make_item(self, user, days_until_expiry, name="Milk"):
        return Item.objects.create(
            user=user,
            category=self.category,
            item_name=name,
            expiry_date=self.today + timedelta(days=days_until_expiry),
        )

    def test_expiry_status(self):
        self.assertEqual(self.make_item(self.user, -1).expiry_status(), "expired")
        self.assertEqual(self.make_item(self.user, 0).expiry_status(), "soon")
        self.assertEqual(self.make_item(self.user, 7).expiry_status(), "soon")
        self.assertEqual(self.make_item(self.user, 8).expiry_status(), "ok")

    def test_negative_price_is_rejected(self):
        response = self.client.post(reverse("item_add"), {
            "item_name": "Milk",
            "category": self.category.pk,
            "price": "-5",
            "expiry_date": self.today,
        })
        self.assertContains(response, "cannot be negative")
        self.assertEqual(Item.objects.count(), 0)

    def test_predefined_category_cannot_be_edited_or_deleted(self):
        self.assertTrue(self.category.is_predefined)
        response = self.client.get(reverse("category_list"))
        self.assertNotContains(response, reverse("category_edit", args=[self.category.pk]))

        self.client.post(reverse("category_edit", args=[self.category.pk]), {
            "category_name": "Changed", "description": "",
        })
        self.client.post(reverse("category_delete", args=[self.category.pk]))
        self.category.refresh_from_db()
        self.assertEqual(self.category.category_name, "Dairy & eggs")

    def test_add_item_with_photo(self):
        response = self.client.post(reverse("item_add"), {
            "item_name": "Milk",
            "category": self.category.pk,
            "price": "95.50",
            "purchase_date": self.today,
            "expiry_date": self.today + timedelta(days=3),
            "photo": make_test_photo(),
        })
        item = Item.objects.get(item_name="Milk")
        self.assertRedirects(response, reverse("item_detail", args=[item.pk]))
        self.assertEqual(item.user, self.user)  # owner set by the view
        self.assertEqual(item.price, 95.5)
        self.assertTrue(item.photo.name.startswith("items/"))

        # The photo is shown on the list and detail pages.
        self.assertContains(self.client.get(reverse("item_list")), item.photo.url)
        self.assertContains(self.client.get(reverse("item_detail", args=[item.pk])), item.photo.url)

    def test_expiry_before_purchase_is_an_error(self):
        response = self.client.post(reverse("item_add"), {
            "item_name": "Milk",
            "category": self.category.pk,
            "purchase_date": self.today,
            "expiry_date": self.today - timedelta(days=1),
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "cannot be before the purchase date")
        self.assertEqual(Item.objects.count(), 0)

    def test_edit_and_delete_item(self):
        item = self.make_item(self.user, 10)
        response = self.client.post(reverse("item_edit", args=[item.pk]), {
            "item_name": "Yogurt",
            "category": self.category.pk,
            "price": "40",
            "expiry_date": self.today + timedelta(days=5),
        })
        self.assertRedirects(response, reverse("item_detail", args=[item.pk]))
        item.refresh_from_db()
        self.assertEqual(item.item_name, "Yogurt")

        response = self.client.post(reverse("item_delete", args=[item.pk]))
        self.assertRedirects(response, reverse("item_list"))
        self.assertFalse(Item.objects.filter(pk=item.pk).exists())

    def test_user_only_sees_own_items(self):
        self.make_item(self.user, 10, name="My milk")
        self.make_item(self.other, 10, name="Sam's bread")
        response = self.client.get(reverse("item_list"))
        self.assertContains(response, "My milk")
        self.assertNotContains(response, "Sam&#x27;s bread")

    def test_cannot_open_edit_or_delete_another_users_item(self):
        others_item = self.make_item(self.other, 10)
        for name in ["item_detail", "item_edit", "item_delete"]:
            response = self.client.get(reverse(name, args=[others_item.pk]))
            self.assertEqual(response.status_code, 404, name)
        self.client.post(reverse("item_delete", args=[others_item.pk]))
        self.assertTrue(Item.objects.filter(pk=others_item.pk).exists())

    def test_dashboard_counts(self):
        self.make_item(self.user, -2)
        self.make_item(self.user, 3)
        self.make_item(self.user, 30)
        self.make_item(self.other, -5)  # someone else's, must not be counted
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.context["total_items"], 3)
        self.assertEqual(response.context["expired_count"], 1)
        self.assertEqual(response.context["soon_count"], 1)

    def test_category_crud_and_protected_delete(self):
        self.client.post(reverse("category_add"), {"category_name": "Pet food", "description": ""})
        category = Category.objects.get(category_name="Pet food")

        self.client.post(reverse("category_edit", args=[category.pk]), {
            "category_name": "Pet supplies", "description": "Food and medicine for pets",
        })
        category.refresh_from_db()
        self.assertEqual(category.category_name, "Pet supplies")

        # A category used by an item cannot be deleted.
        item = self.make_item(self.user, 10)
        item.category = category
        item.save()
        response = self.client.post(reverse("category_delete", args=[category.pk]), follow=True)
        self.assertContains(response, "cannot be deleted")
        self.assertTrue(Category.objects.filter(pk=category.pk).exists())

        # Once no item uses it, deleting works.
        Item.objects.all().delete()
        self.client.post(reverse("category_delete", args=[category.pk]))
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())
