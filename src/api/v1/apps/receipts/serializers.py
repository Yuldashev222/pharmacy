from rest_framework import serializers

from .models import Receipt


class WorkerReceiptCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = ['id', 'price', 'creator']
        read_only_fields = ['creator']


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
