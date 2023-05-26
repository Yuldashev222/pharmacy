from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from ..models import DebtRepayToPharmacy


class DebtRepayToPharmacySerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    from_debt_name = serializers.StringRelatedField(source='from_debt', read_only=True)
    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)
    is_client = serializers.BooleanField(source='from_debt.is_client', read_only=True)
    remaining_debt = serializers.IntegerField(source='from_debt.remaining_debt', read_only=True)
    total_debt = serializers.IntegerField(source='from_debt.price', read_only=True)

    def create(self, validated_data):
        from_debt = validated_data['from_debt']
        if from_debt.is_paid:
            raise ValidationError({'from_debt': 'not found'})
        from_debt.remaining_debt -= validated_data['price']
        if from_debt.remaining_debt <= 0:
            from_debt.is_paid = True
        from_debt.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        price = validated_data.get('price')
        if price and price != instance.price:
            difference = price - instance.price
            from_debt = instance.from_debt
            from_debt.remaining_debt -= difference
            if from_debt.remaining_debt <= 0:
                from_debt.is_paid = True
            else:
                from_debt.is_paid = False
            from_debt.save()
        return super().update(instance, validated_data)


class DirectorManagerDebtRepayToPharmacySerializer(DebtRepayToPharmacySerializer):
    class Meta:
        model = DebtRepayToPharmacy
        fields = '__all__'

    def validate(self, attrs):
        user = self.context['request'].user
        if attrs.get('from_debt') and attrs['from_debt'].from_pharmacy.director_id != user.director_id:
            raise ValidationError({'from_pharmacy': 'not found'})
        return super().validate(attrs)


class WorkerDebtRepayToPharmacySerializer(DebtRepayToPharmacySerializer):
    class Meta:
        model = DebtRepayToPharmacy
        fields = '__all__'
        read_only_fields = ('report_date', 'shift')
