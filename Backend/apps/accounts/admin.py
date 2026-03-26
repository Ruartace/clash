from django.contrib import admin
from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'account_type', 'balance', 'currency', 'created_at')
    list_filter = ('account_type',)
    search_fields = ('user__email', 'name')
