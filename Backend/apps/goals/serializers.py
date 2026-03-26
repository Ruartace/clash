from rest_framework import serializers
from .models import Goal


class GoalSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Goal
        fields = (
            'id', 'name', 'target_amount', 'current_amount',
            'deadline', 'status', 'note', 'progress', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_progress(self, obj):
        if obj.target_amount == 0:
            return '0.00'
        return str(round(obj.current_amount / obj.target_amount * 100, 2))
