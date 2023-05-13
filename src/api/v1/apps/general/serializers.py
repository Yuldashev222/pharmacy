from rest_framework import serializers

from .models import TransferMoneyType


class TransferMoneyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferMoneyType
        exclude = ('director',)
