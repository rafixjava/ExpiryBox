from django.contrib import admin

from .models import Category, Item


class CategoryAdmin(admin.ModelAdmin):
    # Columns shown in the list of categories
    list_display = ["category_name", "description", "is_predefined"]


class ItemAdmin(admin.ModelAdmin):
    # Columns shown in the list of items
    list_display = ["item_name", "user", "category", "price", "expiry_date"]
    # A filter box on the right side
    list_filter = ["category"]
    # A search box at the top
    search_fields = ["item_name", "provider", "reference_number"]


admin.site.register(Category, CategoryAdmin)
admin.site.register(Item, ItemAdmin)
