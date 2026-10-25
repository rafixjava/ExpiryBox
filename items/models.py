# App 2: Items
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# An item is "expiring soon" if it expires within this many days.
EXPIRING_SOON_DAYS = 7


class Category(models.Model):
    # CATEGORY in the class diagram: pk, categoryName, Description
    # Categories are shared by all users.
    category_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    # True for the categories that come with the app (Groceries, Medicine...).
    # Users cannot edit or delete these. Categories that users add have False.
    is_predefined = models.BooleanField(default=False)

    class Meta:
        ordering = ["category_name"]
        verbose_name_plural = "categories"

    def __str__(self):
        return self.category_name


class Item(models.Model):
    # ITEM in the class diagram: pk, user, category, itemName, description,
    # provider, purchaseDate, expiryDate, referenceNumber, createdAt, updatedAt
    # We also added: price and photo.

    # Each item belongs to one user. If the user is deleted, their items are deleted too.
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # Each item belongs to one category.
    # PROTECT means: a category cannot be deleted while an item still uses it.
    category = models.ForeignKey(Category, on_delete=models.PROTECT)

    item_name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    provider = models.CharField(max_length=150, blank=True, help_text="Shop, brand or company.")
    purchase_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField()
    reference_number = models.CharField(max_length=100, blank=True, help_text="Batch, receipt or policy number.")
    price = models.FloatField(default=0, help_text="How much the item cost (in Taka).")
    photo = models.ImageField(upload_to="items/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # filled in once, when the item is created
    updated_at = models.DateTimeField(auto_now=True)      # filled in every time the item is saved

    class Meta:
        ordering = ["expiry_date"]

    def __str__(self):
        return self.item_name

    def days_left(self):
        # How many days until the item expires. A negative number means it already expired.
        today = timezone.localdate()
        difference = self.expiry_date - today
        return difference.days

    def expiry_status(self):
        # Returns "expired", "soon" or "ok".
        days = self.days_left()
        if days < 0:
            return "expired"
        elif days <= EXPIRING_SOON_DAYS:
            return "soon"
        else:
            return "ok"
