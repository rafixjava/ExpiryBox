from django import forms

from .models import ImpactRecord


class ImpactRecordForm(forms.ModelForm):
    class Meta:
        model = ImpactRecord
        # "amount_value" is not here. The view copies it from the item's price.
        fields = ["item", "outcome", "resolved_date", "notes"]
        widgets = {
            "resolved_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_item(self):
        # An item can only have ONE outcome (it is either saved or lost).
        item = self.cleaned_data["item"]

        records_for_this_item = ImpactRecord.objects.filter(item=item)
        # When editing, ignore the record we are editing right now.
        if self.instance.pk:
            records_for_this_item = records_for_this_item.exclude(pk=self.instance.pk)

        if records_for_this_item.exists():
            raise forms.ValidationError("This item already has an outcome recorded.")
        return item

# Note: in views.py we change the "item" drop-down so it only shows the
# logged-in user's own items.
