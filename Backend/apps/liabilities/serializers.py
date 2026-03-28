from rest_framework import serializers

from .models import Liability


class LiabilitySerializer(serializers.ModelSerializer):
    # 前端字段兼容
    principal = serializers.DecimalField(
        source='total_amount',
        max_digits=15,
        decimal_places=2,
        required=False,
    )
    monthly_payment = serializers.DecimalField(
        source='remaining_amount',
        max_digits=15,
        decimal_places=2,
        required=False,
    )
    description = serializers.CharField(source='note', required=False, allow_blank=True, default='')

    class Meta:
        model = Liability
        fields = (
            'id',
            'name',
            'liability_type',
            'principal',
            'interest_rate',
            'monthly_payment',
            'due_date',
            'description',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_internal_value(self, data):
        mutable = dict(data)

        # 前端消费贷值与后端枚举对齐
        if mutable.get('liability_type') == 'consumer_loan':
            mutable['liability_type'] = 'personal_loan'

        # 缺省月供/剩余金额时，默认等于本金
        if not mutable.get('monthly_payment'):
            mutable['monthly_payment'] = mutable.get('principal')

        if 'description' not in mutable or mutable.get('description') is None:
            mutable['description'] = ''

        return super().to_internal_value(mutable)

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # 输出给前端时恢复 consumer_loan，避免前端选项不匹配
        if data.get('liability_type') == 'personal_loan':
            data['liability_type'] = 'consumer_loan'

        return data
