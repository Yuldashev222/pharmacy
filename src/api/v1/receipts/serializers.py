from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Receipt


class WorkerReceiptCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ['id', 'price', 'creator']
        read_only_fields = ['creator']

    def create(self, validated_data):
        data = {
            'pharmacy_id': validated_data['pharmacy_id'],
            'shift': validated_data['shift'],
            'report_date': validated_data['report_date'],
        }
        if Receipt.objects.filter(**data).exists():
            raise ValidationError({'detail': 'The fields pharmacy, shift, report_date must make a unique set.'})
        return super().create(validated_data)


class DirectorManagerReceiptCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = '__all__'
        read_only_fields = ['creator']
        extra_kwargs = {
            'pharmacy': {'write_only': True},
            'report_date': {'write_only': True},
            'shift': {'write_only': True},
        }
