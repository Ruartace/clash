from django.db.models import Sum
from rest_framework import serializers

from apps.transactions.models import Transaction
from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    spent = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = (
            'id',
            'category',
            'amount',
            'month',
            'year',
            'spent',
            'note',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'spent')

    def to_internal_value(self, data):
        mutable = dict(data)

        # 前端 month 以 YYYY-MM 传入，拆分为 year/month
        month_text = mutable.get('month')
        if isinstance(month_text, str) and '-' in month_text:
            y, m = month_text.split('-', 1)
            mutable['year'] = int(y)
            mutable['month'] = int(m)

        return super().to_internal_value(mutable)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['month'] = f"{instance.year:04d}-{instance.month:02d}"
        data.pop('year', None)
        return data

    def get_spent(self, obj: Budget) -> str:
        spent = Transaction.objects.filter(
            user=obj.user,
            category=obj.category,
            transaction_type='expense',
            transaction_date__year=obj.year,
            transaction_date__month=obj.month,
            is_deleted=False,
        ).aggregate(total=Sum('amount'))['total'] or 0
        return str(spent)
