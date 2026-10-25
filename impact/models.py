# App 4: Impact
from django.contrib.auth.models import User
from django.db import models

from items.models import Item

# OUTCOMESTATUS in the class diagram: an item was either SAVED or LOST.
OUTCOME_CHOICES = [
    ("SAVED", "Saved (used before it expired)"),
    ("LOST", "Lost (it expired / was wasted)"),
]


class ImpactRecord(models.Model):
    # IMPACTRECORD in the class diagram: pk, item, outcome, amountValue,
    # resolvedDate, notes, createdAt
    # Note: the diagram shows "notes" as bool. We use a text field so the user
    # can write a short note.

    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES)
    # amount_value is copied from the item's price (see impact/views.py).
    amount_value = models.FloatField(default=0)
    resolved_date = models.DateField()
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-resolved_date"]

    def __str__(self):
        return str(self.item) + " - " + self.outcome


class ImpactSummary(models.Model):
    # IMPACTSUMMARY in the class diagram: pk, user, year
    # The totals are not saved here. The summary page adds them up from the
    # impact records every time, so they are always correct.

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()

    class Meta:
        ordering = ["-year"]
        unique_together = ["user", "year"]  # only one summary per user per year
        verbose_name_plural = "impact summaries"

    def __str__(self):
        return str(self.user) + " - " + str(self.year)
