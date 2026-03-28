from datetime import date

from rest_framework import serializers

from .models import Asset


class AssetSerializer(serializers.ModelSerializer):
    # 与前端字段对齐：purchase_price -> model.purchase_value
    purchase_price = serializers.DecimalField(
        source='purchase_value',
        max_digits=15,
        decimal_places=2,
        required=False,
    )
    # 与前端字段对齐：description -> model.note
    description = serializers.CharField(source='note', required=False, allow_blank=True, default='')

    class Meta:
        model = Asset
        fields = (
            'id',
            'name',
            'asset_type',
            'current_value',
            'purchase_price',
            'purchase_date',
            'description',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_internal_value(self, data):
        mutable = dict(data)

        # 前端可能不传购入价格：默认等于当前价值
        if not mutable.get('purchase_price'):
            mutable['purchase_price'] = mutable.get('current_value')

        # 前端可能不传购入日期：默认今天
        if not mutable.get('purchase_date'):
            mutable['purchase_date'] = date.today().isoformat()

        # 描述缺省为空字符串
        if 'description' not in mutable or mutable.get('description') is None:
            mutable['description'] = ''

        return super().to_internal_value(mutable)
