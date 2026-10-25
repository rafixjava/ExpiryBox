from django.contrib import admin

from .models import Notification, Reminder


class ReminderAdmin(admin.ModelAdmin):
    list_display = ["item", "reminder_date", "reminder_type", "is_sent"]
    list_filter = ["reminder_type", "is_sent"]


class NotificationAdmin(admin.ModelAdmin):
    list_display = ["message", "user", "notification_type", "is_read", "created_at"]
    list_filter = ["notification_type", "is_read"]


admin.site.register(Reminder, ReminderAdmin)
admin.site.register(Notification, NotificationAdmin)
