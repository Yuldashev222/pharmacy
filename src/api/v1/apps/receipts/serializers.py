from rest_framework import serializers

from .models import Receipt


class ReceiptReportSerializer(serializers.Serializer):
    class Meta:
        model = Receipt
        fields = []


class WorkerReceiptCreateUpdateSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Receipt
        fields = ['id', 'price', 'creator']


class DirectorManagerReceiptCreateUpdateSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Receipt
        fields = '__all__'
        extra_kwargs = {
            'pharmacy': {'write_only': True},
            'report_date': {'write_only': True},
            'shift': {'write_only': True},
        }
