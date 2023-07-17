from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Drug


class WorkerDrugSerializer(serializers.ModelSerializer):
    pharmacy_name = serializers.StringRelatedField(source='pharmacy', read_only=True)

    class Meta:
        model = Drug
        fields = '__all__'
        read_only_fields = ('pharmacy',)

    def validate(self, attrs):
        pharmacy = attrs.get('pharmacy')
        if pharmacy and pharmacy.director_id != self.context['request'].user.director_id:
            raise ValidationError({'pharmacy': 'not found'})
        return attrs


class DirectorManagerDrugSerializer(WorkerDrugSerializer):
    class Meta(WorkerDrugSerializer.Meta):
        read_only_fields = []
