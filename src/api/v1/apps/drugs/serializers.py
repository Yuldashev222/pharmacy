from rest_framework import serializers

from .models import Drug


class WorkerDrugSerializer(serializers.ModelSerializer):
    pharmacy_name = serializers.StringRelatedField(source='pharmacy', read_only=True)

    class Meta:
        model = Drug
        fields = '__all__'
        read_only_fields = ('pharmacy',)


class DirectorManagerDrugSerializer(serializers.ModelSerializer):
    pharmacy_name = serializers.StringRelatedField(source='pharmacy', read_only=True)

    class Meta:
        model = Drug
        fields = '__all__'
