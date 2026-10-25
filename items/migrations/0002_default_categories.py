# Adds a few starting categories so new users can add items straight away.
from django.db import migrations

CATEGORIES = [
    ("Groceries", "Rice, flour, lentils, snacks and other pantry food."),
    ("Dairy & eggs", "Milk, yogurt, cheese, butter, eggs."),
    ("Fruit & vegetables", "Fresh produce."),
    ("Bakery", "Bread, cakes, biscuits."),
    ("Beverages", "Juice, soft drinks, tea, coffee."),
    ("Frozen", "Frozen meat, fish, ready meals."),
    ("Medicine", "Tablets, syrups, first-aid supplies."),
    ("Personal care", "Cosmetics, skincare, toiletries."),
    ("Household", "Cleaning supplies, batteries, filters."),
    ("Documents & warranties", "Passports, licences, warranties, subscriptions."),
]


def add_categories(apps, schema_editor):
    Category = apps.get_model("items", "Category")
    for name, description in CATEGORIES:
        Category.objects.get_or_create(category_name=name, defaults={"description": description})


def remove_categories(apps, schema_editor):
    Category = apps.get_model("items", "Category")
    for name, description in CATEGORIES:
        Category.objects.filter(category_name=name, item__isnull=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("items", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_categories, remove_categories),
    ]
