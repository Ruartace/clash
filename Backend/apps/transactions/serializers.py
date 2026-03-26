from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            'id', 'account', 'transaction_type', 'amount',
            'category', 'note', 'transaction_date', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
