from django import forms

from .models import Category, Item


class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        # We don't list "user" here. The view fills it in with the logged-in user.
        fields = [
            "item_name",
            "category",
            "price",
            "description",
            "provider",
            "purchase_date",
            "expiry_date",
            "reference_number",
            "photo",
        ]
        widgets = {
            # type="date" shows a calendar to pick the date.
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "expiry_date": forms.DateInput(attrs={"type": "date"}),
            "price": forms.NumberInput(attrs={"min": "0", "step": "0.01"}),
            "description": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "price": "Price (Tk)",
        }

    def clean(self):
        # clean() runs after Django has checked each field.
        cleaned_data = super().clean()
        price = cleaned_data.get("price")
        purchase_date = cleaned_data.get("purchase_date")
        expiry_date = cleaned_data.get("expiry_date")

        if price is not None and price < 0:
            self.add_error("price", "The price cannot be negative.")

        if purchase_date and expiry_date:
            if expiry_date < purchase_date:
                self.add_error("expiry_date", "The expiry date cannot be before the purchase date.")

        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        # "is_predefined" is not here, so users can never make a predefined category.
        fields = ["category_name", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }
