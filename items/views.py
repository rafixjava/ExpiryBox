from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from impact.models import ImpactRecord
from notifications.models import Notification, Reminder
from notifications.views import create_due_notifications

from .forms import CategoryForm, ItemForm
from .models import Category, Item


def home(request):
    # The home page just opens the dashboard.
    # (@login_required on the dashboard sends visitors to the login page.)
    return redirect("dashboard")


@login_required
def dashboard(request):
    # First, turn reminders whose date has arrived into notifications.
    create_due_notifications(request.user)

    # All items of the logged-in user
    items = Item.objects.filter(user=request.user)

    # Count expired items and collect the items that expire soon
    expired_count = 0
    soon_items = []
    for item in items:
        if item.expiry_status() == "expired":
            expired_count = expired_count + 1
        elif item.expiry_status() == "soon":
            soon_items.append(item)

    # Count saved and lost outcomes
    saved_count = ImpactRecord.objects.filter(item__user=request.user, outcome="SAVED").count()
    lost_count = ImpactRecord.objects.filter(item__user=request.user, outcome="LOST").count()

    # The next 5 reminders that are still waiting
    today = timezone.localdate()
    upcoming_reminders = Reminder.objects.filter(item__user=request.user, is_sent=False, reminder_date__gte=today)
    upcoming_reminders = upcoming_reminders.order_by("reminder_date")[:5]

    # The 5 newest notifications
    recent_notifications = Notification.objects.filter(user=request.user)[:5]

    context = {
        "total_items": items.count(),
        "expired_count": expired_count,
        "soon_count": len(soon_items),
        "soon_items": soon_items,
        "saved_count": saved_count,
        "lost_count": lost_count,
        "upcoming_reminders": upcoming_reminders,
        "recent_notifications": recent_notifications,
    }
    return render(request, "items/dashboard.html", context)


# ------------------------------------------------------------------ Items

@login_required
def item_list(request):
    # Only show the items of the logged-in user.
    items = Item.objects.filter(user=request.user)
    return render(request, "items/item_list.html", {"items": items})


@login_required
def item_detail(request, pk):
    # user=request.user makes sure nobody can open another user's item.
    # If the item is not theirs, they get a "404 Page not found".
    item = get_object_or_404(Item, pk=pk, user=request.user)
    reminders = Reminder.objects.filter(item=item)
    impact_records = ImpactRecord.objects.filter(item=item)

    context = {
        "item": item,
        "reminders": reminders,
        "impact_records": impact_records,
    }
    return render(request, "items/item_detail.html", context)


@login_required
def item_add(request):
    if request.method == "POST":
        # request.FILES contains the uploaded photo.
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)  # create the item, but don't save it yet
            item.user = request.user        # the owner is the logged-in user
            item.save()                     # now save it to the database
            messages.success(request, "Item added.")
            return redirect("item_detail", pk=item.pk)
    else:
        form = ItemForm()

    return render(request, "items/item_form.html", {"form": form, "title": "Add item"})


@login_required
def item_edit(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)

    if request.method == "POST":
        form = ItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save()

            # If the price changed, update the amount of this item's impact record too.
            records = ImpactRecord.objects.filter(item=item)
            for record in records:
                record.amount_value = item.price
                record.save()

            messages.success(request, "Item updated.")
            return redirect("item_detail", pk=item.pk)
    else:
        form = ItemForm(instance=item)

    return render(request, "items/item_form.html", {"form": form, "title": "Edit item"})


@login_required
def item_delete(request, pk):
    item = get_object_or_404(Item, pk=pk, user=request.user)

    if request.method == "POST":
        # Its reminders, notifications and impact records are deleted too (CASCADE).
        item.delete()
        messages.success(request, "Item deleted.")
        return redirect("item_list")

    return render(request, "items/item_confirm_delete.html", {"item": item})


# ------------------------------------------------------------------ Categories
# Categories are shared by all users.
# Predefined categories (is_predefined=True) cannot be edited or deleted.

@login_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, "items/category_list.html", {"categories": categories})


@login_required
def category_add(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category added.")
            return redirect("category_list")
    else:
        form = CategoryForm()

    return render(request, "items/category_form.html", {"form": form, "title": "Add category"})


@login_required
def category_edit(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if category.is_predefined:
        messages.error(request, "Predefined categories cannot be edited.")
        return redirect("category_list")

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("category_list")
    else:
        form = CategoryForm(instance=category)

    return render(request, "items/category_form.html", {"form": form, "title": "Edit category"})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if category.is_predefined:
        messages.error(request, "Predefined categories cannot be deleted.")
        return redirect("category_list")

    if request.method == "POST":
        # A category that is still used by an item cannot be deleted.
        if Item.objects.filter(category=category).exists():
            messages.error(request, "This category is still used by items, so it cannot be deleted.")
        else:
            category.delete()
            messages.success(request, "Category deleted.")
        return redirect("category_list")

    return render(request, "items/category_confirm_delete.html", {"category": category})
