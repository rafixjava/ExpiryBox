# App 3: Notifications
#
# Reminder     = a date the user saves: "remind me about this item on this day".
# Notification = the message the app creates when that date arrives.
from django.contrib.auth.models import User
from django.db import models

from items.models import Item

REMINDER_TYPE_CHOICES = [
    ("WEEK_BEFORE", "One week before expiry"),
    ("DAY_BEFORE", "One day before expiry"),
    ("ON_EXPIRY", "On the expiry day"),
    ("CUSTOM", "Custom date"),
]

NOTIFICATION_TYPE_CHOICES = [
    ("REMINDER", "Reminder"),
    ("EXPIRED", "Item expired"),
]


class Reminder(models.Model):
    # REMINDER in the class diagram: pk, item, reminderDate, reminderType, isSent, createdAt

    # One item can have many reminders. If the item is deleted, its reminders are deleted too.
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    reminder_date = models.DateField()
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPE_CHOICES, default="CUSTOM")
    # False = still waiting. True = the notification for it has been created.
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["reminder_date"]

    def __str__(self):
        return str(self.item) + " on " + str(self.reminder_date)


class Notification(models.Model):
    # NOTIFICATION in the class diagram: pk, user, item, message, notificationType, isRead, createdAt

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # The item is optional (null=True, blank=True).
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default="REMINDER")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # the minus sign means newest first

    def __str__(self):
        return self.message
