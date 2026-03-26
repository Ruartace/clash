from django.contrib import admin
from .models import Liability


@admin.register(Liability)
class LiabilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'liability_type', 'remaining_amount', 'due_date')
    list_filter = ('liability_type',)
    search_fields = ('user__email', 'name')
