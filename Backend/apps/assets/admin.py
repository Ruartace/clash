from django.contrib import admin
from .models import Asset


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'asset_type', 'current_value', 'purchase_date')
    list_filter = ('asset_type',)
    search_fields = ('user__email', 'name')
