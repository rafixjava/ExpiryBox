from django.urls import path

from . import views

urlpatterns = [
    path("reminders/", views.reminder_list, name="reminder_list"),
    path("reminders/add/", views.reminder_add, name="reminder_add"),
    path("reminders/<int:pk>/edit/", views.reminder_edit, name="reminder_edit"),
    path("reminders/<int:pk>/delete/", views.reminder_delete, name="reminder_delete"),
    path("notifications/", views.notification_list, name="notification_list"),
    path("notifications/<int:pk>/read/", views.notification_mark_read, name="notification_mark_read"),
    path("notifications/<int:pk>/delete/", views.notification_delete, name="notification_delete"),
]
