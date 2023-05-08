from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import TransferMoneyType, ExpenseType


class TransferMoneyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferMoneyType
        exclude = ('director',)


class ExpenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseType
        exclude = ('director',)
