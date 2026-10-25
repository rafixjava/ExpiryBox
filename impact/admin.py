from django.contrib import admin

from .models import ImpactRecord, ImpactSummary


class ImpactRecordAdmin(admin.ModelAdmin):
    list_display = ["item", "outcome", "amount_value", "resolved_date"]
    list_filter = ["outcome"]


class ImpactSummaryAdmin(admin.ModelAdmin):
    list_display = ["user", "year"]


admin.site.register(ImpactRecord, ImpactRecordAdmin)
admin.site.register(ImpactSummary, ImpactSummaryAdmin)
