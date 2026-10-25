from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from items.models import Category, Item

from .models import ImpactRecord, ImpactSummary


class ImpactTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("riya", "riya@example.com", "a-Strong-pass-123")
        self.other = User.objects.create_user("sam", "sam@example.com", "a-Strong-pass-123")
        self.category = Category.objects.first()
        self.client.login(username="riya", password="a-Strong-pass-123")

    def make_item(self, user, name, price=0):
        return Item.objects.create(
            user=user, category=self.category, item_name=name,
            expiry_date=date(2026, 1, 1), price=price,
        )

    def test_add_edit_delete_record(self):
        item = self.make_item(self.user, "Milk", price=120.5)
        response = self.client.post(reverse("record_add"), {
            "item": item.pk,
            "outcome": "SAVED",
            "resolved_date": "2026-03-01",
            "notes": "Used it for breakfast.",
        })
        self.assertRedirects(response, reverse("record_list"))
        record = ImpactRecord.objects.get(item=item)
        self.assertEqual(record.amount_value, 120.5)  # copied from the item's price
        self.assertEqual(record.notes, "Used it for breakfast.")

        self.client.post(reverse("record_edit", args=[record.pk]), {
            "item": item.pk,
            "outcome": "LOST",
            "resolved_date": "2026-03-01",
            "notes": "",
        })
        record.refresh_from_db()
        self.assertEqual(record.outcome, "LOST")

        self.client.post(reverse("record_delete", args=[record.pk]))
        self.assertFalse(ImpactRecord.objects.filter(pk=record.pk).exists())

    def test_item_can_only_have_one_outcome(self):
        item = self.make_item(self.user, "Milk")
        ImpactRecord.objects.create(item=item, outcome="SAVED", amount_value=10, resolved_date=date(2026, 1, 1))
        response = self.client.post(reverse("record_add"), {
            "item": item.pk, "outcome": "LOST", "amount_value": "10", "resolved_date": "2026-01-02",
        })
        self.assertContains(response, "already has an outcome recorded")
        self.assertEqual(ImpactRecord.objects.count(), 1)

    def test_editing_item_price_updates_record_amount(self):
        item = self.make_item(self.user, "Milk", price=50)
        record = ImpactRecord.objects.create(item=item, outcome="LOST", amount_value=50, resolved_date=date(2026, 1, 2))
        self.client.post(reverse("item_edit", args=[item.pk]), {
            "item_name": "Milk", "category": self.category.pk,
            "price": "80", "expiry_date": "2026-01-01",
        })
        record.refresh_from_db()
        self.assertEqual(record.amount_value, 80)

    def test_yearly_summary_totals(self):
        def record(user, name, outcome, amount, resolved):
            ImpactRecord.objects.create(
                item=self.make_item(user, name), outcome=outcome,
                amount_value=amount, resolved_date=resolved,
            )

        record(self.user, "A", "SAVED", 100, date(2026, 2, 1))
        record(self.user, "B", "SAVED", 50, date(2026, 5, 1))
        record(self.user, "C", "LOST", 30, date(2026, 6, 1))
        record(self.user, "D", "LOST", 20, date(2025, 6, 1))
        record(self.other, "E", "SAVED", 999, date(2026, 1, 1))  # someone else's

        response = self.client.get(reverse("impact_summary"))
        rows = response.context["rows"]
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0], {"year": 2026, "saved_total": 150, "lost_total": 30, "saved_count": 2, "lost_count": 1})
        self.assertEqual(rows[1], {"year": 2025, "saved_total": 0, "lost_total": 20, "saved_count": 0, "lost_count": 1})
        self.assertEqual(ImpactSummary.objects.filter(user=self.user).count(), 2)

    def test_other_users_records_are_protected(self):
        others_record = ImpactRecord.objects.create(
            item=self.make_item(self.other, "Bread"), outcome="LOST",
            amount_value=5, resolved_date=date(2026, 1, 1),
        )
        self.assertEqual(self.client.get(reverse("record_edit", args=[others_record.pk])).status_code, 404)
        self.assertEqual(self.client.post(reverse("record_delete", args=[others_record.pk])).status_code, 404)
        self.assertNotContains(self.client.get(reverse("record_list")), "Bread")
