from datetime import date

from rest_framework import serializers

from .models import FlowRecord


class FlowRecordSerializer(serializers.ModelSerializer):
    description = serializers.CharField(source='note', required=False, allow_blank=True, default='')

    class Meta:
        model = FlowRecord
        fields = (
            'id',
            'source_name',
            'source_type',
            'target_name',
            'target_type',
            'amount',
            'flow_date',
            'description',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_internal_value(self, data):
        mutable = dict(data)

        if not mutable.get('flow_date'):
            mutable['flow_date'] = date.today().isoformat()

        if 'description' not in mutable or mutable.get('description') is None:
            mutable['description'] = ''

        return super().to_internal_value(mutable)
