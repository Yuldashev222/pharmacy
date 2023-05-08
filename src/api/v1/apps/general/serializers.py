from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import TransferMoneyType, ExpenseType


class DirectorTransferMoneyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferMoneyType
        fields = '__all__'

    def validate_company(self, obj):
        if obj not in self.context['request'].user.companies.all():
            raise ValidationError('not found')
        return obj


class EmployeeTransferMoneyTypeSerializer(DirectorTransferMoneyTypeSerializer):
    class Meta(DirectorTransferMoneyTypeSerializer.Meta):
        exclude = ('company',)


class DirectorExpenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseType
        exclude = ('is_expense_type',)

    def validate_company(self, obj):
        if obj not in self.context['request'].user.companies.all():
            raise ValidationError('not found')
        return obj


class EmployeeExpenseTypeSerializer(DirectorExpenseTypeSerializer):
    class Meta(DirectorExpenseTypeSerializer.Meta):
        exclude = ('company', 'is_expense_type')
