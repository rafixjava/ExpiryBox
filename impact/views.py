from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from items.models import Item

from .forms import ImpactRecordForm
from .models import ImpactRecord, ImpactSummary


@login_required
def record_list(request):
    # An impact record belongs to a user through its item: record.item.user
    records = ImpactRecord.objects.filter(item__user=request.user)
    return render(request, "impact/record_list.html", {"records": records})


@login_required
def record_add(request):
    if request.method == "POST":
        form = ImpactRecordForm(request.POST)
    else:
        form = ImpactRecordForm()
        form.initial["resolved_date"] = timezone.localdate()

        # The item page links here with ?item=5 so that item is already selected.
        item_id = request.GET.get("item")
        if item_id:
            form.initial["item"] = item_id

    # Only show the logged-in user's items in the drop-down list.
    form.fields["item"].queryset = Item.objects.filter(user=request.user)

    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False)
        # The amount saved or lost is the price of the item.
        record.amount_value = record.item.price
        record.save()
        messages.success(request, "Outcome recorded.")
        return redirect("record_list")

    return render(request, "impact/record_form.html", {"form": form, "title": "Record an outcome"})


@login_required
def record_edit(request, pk):
    record = get_object_or_404(ImpactRecord, pk=pk, item__user=request.user)

    if request.method == "POST":
        form = ImpactRecordForm(request.POST, instance=record)
    else:
        form = ImpactRecordForm(instance=record)

    # Only show the logged-in user's items in the drop-down list.
    form.fields["item"].queryset = Item.objects.filter(user=request.user)

    if request.method == "POST" and form.is_valid():
        record = form.save(commit=False)
        record.amount_value = record.item.price
        record.save()
        messages.success(request, "Outcome updated.")
        return redirect("record_list")

    return render(request, "impact/record_form.html", {"form": form, "title": "Edit outcome"})


@login_required
def record_delete(request, pk):
    record = get_object_or_404(ImpactRecord, pk=pk, item__user=request.user)

    if request.method == "POST":
        record.delete()
        messages.success(request, "Outcome deleted.")
        return redirect("record_list")

    return render(request, "impact/record_confirm_delete.html", {"record": record})


@login_required
def summary(request):
    records = ImpactRecord.objects.filter(item__user=request.user)

    # Step 1: make a list of every year that has at least one record.
    years = []
    for record in records:
        year = record.resolved_date.year
        if year not in years:
            years.append(year)

    # Step 2: make sure there is one ImpactSummary for each of those years...
    for year in years:
        ImpactSummary.objects.get_or_create(user=request.user, year=year)

    # ...and delete summaries for years that no longer have any records.
    old_summaries = ImpactSummary.objects.filter(user=request.user).exclude(year__in=years)
    old_summaries.delete()

    # Step 3: add up the totals for each year.
    rows = []
    summaries = ImpactSummary.objects.filter(user=request.user)
    for summary_row in summaries:
        saved_total = 0
        lost_total = 0
        saved_count = 0
        lost_count = 0

        records_this_year = records.filter(resolved_date__year=summary_row.year)
        for record in records_this_year:
            if record.outcome == "SAVED":
                saved_total = saved_total + record.amount_value
                saved_count = saved_count + 1
            else:
                lost_total = lost_total + record.amount_value
                lost_count = lost_count + 1

        rows.append({
            "year": summary_row.year,
            "saved_total": saved_total,
            "lost_total": lost_total,
            "saved_count": saved_count,
            "lost_count": lost_count,
        })

    return render(request, "impact/summary.html", {"rows": rows})
