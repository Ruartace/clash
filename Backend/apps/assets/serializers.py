from rest_framework import serializers
from .models import Asset


class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = (
            'id', 'name', 'asset_type', 'current_value',
            'purchase_value', 'purchase_date', 'note', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
