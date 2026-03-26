from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'transaction_type', 'amount', 'category', 'transaction_date')
    list_filter = ('transaction_type', 'category')
    search_fields = ('user__email', 'note')
