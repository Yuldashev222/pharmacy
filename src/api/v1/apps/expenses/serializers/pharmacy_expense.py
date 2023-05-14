from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from api.v1.apps.reports.models import Report

from ..models import PharmacyExpense, ExpenseType


class ExpenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseType
        exclude = ('director',)


class PharmacyExpenseSerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk', view_name='user_expense-detail', read_only=True)

    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator', view_name='user-detail', read_only=True)

    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    from_pharmacy_detail = serializers.HyperlinkedRelatedField(source='from_pharmacy',
                                                               view_name='user-detail', read_only=True)

    to_user_name = serializers.StringRelatedField(source='to_user', read_only=True)
    to_user_detail = serializers.HyperlinkedRelatedField(source='to_user', view_name='user-detail', read_only=True)

    to_pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    to_pharmacy_detail = serializers.HyperlinkedRelatedField(source='to_pharmacy',
                                                             view_name='pharmacy-detail', read_only=True)

    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    transfer_type_detail = serializers.HyperlinkedRelatedField(source='transfer_type',
                                                               view_name='transfer_type-detail', read_only=True)

    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)
    expense_type_detail = serializers.HyperlinkedRelatedField(source='expense_type',
                                                              view_name='expense_type-detail', read_only=True)
    # expense_type = serializers.StringRelatedField(source='income_expense_type', read_only=True)


class WorkerPharmacyExpenseSerializer(PharmacyExpenseSerializer):
    class Meta:
        model = PharmacyExpense
        exclude = ('from_pharmacy',)
        read_only_fields = ('shift',)

    def validate(self, attrs):
        user = self.context['request'].user
        to_user = attrs.get('to_user')

        if to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})

        attrs['shift'] = user.shift
        attrs['report_date'] = date.today()
        attrs['from_pharmacy'] = user.pharmacy
        return attrs


class DirectorManagerPharmacyExpenseSerializer(PharmacyExpenseSerializer):
    class Meta:
        model = PharmacyExpense
        fields = '__all__'
        extra_kwargs = {
            'report_date': {'required': False}
        }

    def create(self, validated_data):
        if not validated_data.get('report_date'):
            raise ValidationError({'report_date': 'This field is required.'})
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        from_pharmacy = attrs['from_pharmacy']
        to_user = attrs.get('to_user')

        if from_pharmacy.director_id != user.director_id:
            raise ValidationError({'from_pharmacy': 'not found'})

        if to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})

        return attrs
