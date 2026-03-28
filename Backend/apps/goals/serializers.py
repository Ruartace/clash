from rest_framework import serializers

from .models import Goal


class GoalSerializer(serializers.ModelSerializer):
    # 前端字段兼容：description <-> note
    description = serializers.CharField(source='note', required=False, allow_blank=True, default='')
    # 前端字段兼容：is_completed 与 status 互转
    is_completed = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = (
            'id',
            'name',
            'target_amount',
            'current_amount',
            'deadline',
            'status',
            'description',
            'is_completed',
            'progress',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_completed', 'progress')

    def to_internal_value(self, data):
        mutable = dict(data)

        # 前端可传 is_completed，映射为 status
        if 'is_completed' in mutable and 'status' not in mutable:
            mutable['status'] = 'completed' if bool(mutable.get('is_completed')) else 'in_progress'

        return super().to_internal_value(mutable)

    def get_is_completed(self, obj: Goal) -> bool:
        return obj.status == 'completed'

    def get_progress(self, obj: Goal) -> str:
        if obj.target_amount == 0:
            return '0.00'
        return str(round(obj.current_amount / obj.target_amount * 100, 2))
