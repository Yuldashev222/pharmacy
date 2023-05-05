from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import TransferMoneyType, IncomeExpenseType


class DirectorTransferMoneyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferMoneyType
        fields = '__all__'

    def validate_company(self, obj):
        if obj not in self.context['request'].user.companies.all():
            raise ValidationError('not found')
        return obj


class EmployeeTransferMoneyTypeSerializer(DirectorTransferMoneyTypeSerializer):
    class Meta:
        model = TransferMoneyType
        exclude = ('company',)


class DirectorIncomeExpenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomeExpenseType
        exclude = ('is_expense_type',)

    def validate_company(self, obj):
        if obj not in self.context['request'].user.companies.all():
            raise ValidationError('not found')
        return obj


class EmployeeIncomeExpenseTypeSerializer(DirectorIncomeExpenseTypeSerializer):
    class Meta:
        model = IncomeExpenseType
        exclude = ('company', 'is_expense_type')
