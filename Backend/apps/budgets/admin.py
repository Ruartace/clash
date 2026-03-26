from django.contrib import admin
from .models import Budget


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'year', 'month')
    list_filter = ('year', 'month')
    search_fields = ('user__email', 'category')
