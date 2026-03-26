from rest_framework import serializers
from .models import Liability


class LiabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Liability
        fields = (
            'id', 'name', 'liability_type', 'total_amount', 'remaining_amount',
            'interest_rate', 'due_date', 'note', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
