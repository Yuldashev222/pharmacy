from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import PharmacyExpense, ExpenseType


class ExpenseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseType
        fields = '__all__'
        read_only_fields = ('director',)


class PharmacyExpenseSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    to_user_name = serializers.StringRelatedField(source='to_user', read_only=True)
    to_pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)

    def validate(self, attrs):
        to_user = attrs.get('to_user')
        if to_user and self.context['request'].user.id == to_user.id:
            raise ValidationError({'to_user': 'not found'})
        return attrs


class WorkerPharmacyExpenseSerializer(PharmacyExpenseSerializer):
    class Meta:
        model = PharmacyExpense
        fields = '__all__'
        read_only_fields = ('shift', 'report_date', 'from_pharmacy')

    def validate(self, attrs):
        user = self.context['request'].user
        to_user = attrs.get('to_user')

        if to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})
        return super().validate(attrs)


class DirectorManagerPharmacyExpenseSerializer(PharmacyExpenseSerializer):
    class Meta:
        model = PharmacyExpense
        fields = '__all__'

    def validate(self, attrs):
        user = self.context['request'].user
        to_user = attrs.get('to_user')
        from_pharmacy = attrs.get('from_pharmacy')
        if from_pharmacy and from_pharmacy.director_id != user.director_id:
            raise ValidationError({'from_pharmacy': 'not found'})

        if to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})

        return super().validate(attrs)
