from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from items.models import Item

from .forms import ReminderForm
from .models import Notification, Reminder


def create_due_notifications(user):
    # Creates a notification for every reminder whose date has arrived.
    #
    # There is no background program. This function runs when the user opens
    # the dashboard or the notifications page. After a reminder creates its
    # notification we set is_sent = True, so it never creates a second one.
    today = timezone.localdate()
    due_reminders = Reminder.objects.filter(item__user=user, is_sent=False, reminder_date__lte=today)

    for reminder in due_reminders:
        item = reminder.item
        days = item.days_left()

        if days < 0:
            message = item.item_name + " expired on " + str(item.expiry_date) + "."
            notification_type = "EXPIRED"
        elif days == 0:
            message = item.item_name + " expires today."
            notification_type = "REMINDER"
        else:
            message = item.item_name + " expires in " + str(days) + " day(s), on " + str(item.expiry_date) + "."
            notification_type = "REMINDER"

        Notification.objects.create(
            user=user,
            item=item,
            message=message,
            notification_type=notification_type,
        )

        reminder.is_sent = True
        reminder.save()


# ------------------------------------------------------------------ Reminders

@login_required
def reminder_list(request):
    # A reminder belongs to a user through its item: reminder.item.user
    reminders = Reminder.objects.filter(item__user=request.user)
    return render(request, "notifications/reminder_list.html", {"reminders": reminders})


@login_required
def reminder_add(request):
    if request.method == "POST":
        form = ReminderForm(request.POST)
    else:
        form = ReminderForm()

        # The item page links here with ?item=5 so that item is already selected.
        item_id = request.GET.get("item")
        if item_id:
            form.initial["item"] = item_id

    # Only show the logged-in user's items in the drop-down list.
    form.fields["item"].queryset = Item.objects.filter(user=request.user)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Reminder saved.")
        return redirect("reminder_list")

    return render(request, "notifications/reminder_form.html", {"form": form, "title": "Add reminder"})


@login_required
def reminder_edit(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, item__user=request.user)

    if request.method == "POST":
        form = ReminderForm(request.POST, instance=reminder)
    else:
        form = ReminderForm(instance=reminder)

    # Only show the logged-in user's items in the drop-down list.
    form.fields["item"].queryset = Item.objects.filter(user=request.user)

    if request.method == "POST" and form.is_valid():
        reminder = form.save(commit=False)
        # The date may have changed, so the reminder should be sent again.
        reminder.is_sent = False
        reminder.save()
        messages.success(request, "Reminder updated.")
        return redirect("reminder_list")

    return render(request, "notifications/reminder_form.html", {"form": form, "title": "Edit reminder"})


@login_required
def reminder_delete(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, item__user=request.user)

    if request.method == "POST":
        reminder.delete()
        messages.success(request, "Reminder deleted.")
        return redirect("reminder_list")

    return render(request, "notifications/reminder_confirm_delete.html", {"reminder": reminder})


# ------------------------------------------------------------------ Notifications

@login_required
def notification_list(request):
    create_due_notifications(request.user)
    notifications = Notification.objects.filter(user=request.user)
    return render(request, "notifications/notification_list.html", {"notifications": notifications})


@login_required
def notification_mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)

    if request.method == "POST":
        notification.is_read = True
        notification.save()

    return redirect("notification_list")


@login_required
def notification_delete(request, pk):
    notification = get_object_or_404(Notification, pk=pk, user=request.user)

    if request.method == "POST":
        notification.delete()
        messages.success(request, "Notification deleted.")

    return redirect("notification_list")
