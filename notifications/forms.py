from django import forms

from .models import Reminder


class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        # "is_sent" is not here. The app changes it, not the user.
        fields = ["item", "reminder_date", "reminder_type"]
        widgets = {
            "reminder_date": forms.DateInput(attrs={"type": "date"}),
        }

# Note: in views.py we change the "item" drop-down so it only shows the
# logged-in user's own items.
