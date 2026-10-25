# Adds Item.price and Category.is_predefined, then marks the starting
# categories (added in 0002_default_categories) as predefined.
from django.db import migrations, models

PREDEFINED_NAMES = [
    "Groceries",
    "Dairy & eggs",
    "Fruit & vegetables",
    "Bakery",
    "Beverages",
    "Frozen",
    "Medicine",
    "Personal care",
    "Household",
    "Documents & warranties",
]


def mark_predefined(apps, schema_editor):
    Category = apps.get_model("items", "Category")
    Category.objects.filter(category_name__in=PREDEFINED_NAMES).update(is_predefined=True)


def unmark_predefined(apps, schema_editor):
    Category = apps.get_model("items", "Category")
    Category.objects.update(is_predefined=False)


class Migration(migrations.Migration):

    dependencies = [
        ("items", "0002_default_categories"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="is_predefined",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="item",
            name="price",
            field=models.FloatField(default=0, help_text="How much the item cost (in Taka)."),
        ),
        migrations.AlterField(
            model_name="category",
            name="category_name",
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name="item",
            name="item_name",
            field=models.CharField(max_length=150),
        ),
        migrations.RunPython(mark_predefined, unmark_predefined),
    ]
