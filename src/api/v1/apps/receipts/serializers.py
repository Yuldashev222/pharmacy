from rest_framework import serializers

from .models import Receipt


class ReceiptReportSerializer(serializers.Serializer):
    class Meta:
        model = Receipt
        fields = []
