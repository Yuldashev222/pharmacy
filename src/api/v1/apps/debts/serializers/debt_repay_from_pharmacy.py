from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import DebtRepayFromPharmacy


class DebtRepayFromPharmacySerializer(serializers.ModelSerializer):
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    to_debt_name = serializers.StringRelatedField(source='to_debt', read_only=True)
    from_user_name = serializers.StringRelatedField(source='from_user', read_only=True)
    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)
    remaining_debt = serializers.IntegerField(source='to_debt.remaining_debt', read_only=True)
    total_debt = serializers.IntegerField(source='to_debt.price', read_only=True)

    def create(self, validated_data):
        to_debt = validated_data['to_debt']
        to_debt.remaining_debt -= validated_data['price']
        if to_debt.remaining_debt <= 0:
            to_debt.is_paid = True
        to_debt.save()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        price = validated_data.get('price')
        if price and price != instance.price:
            difference = price - instance.price
            to_debt = instance.to_debt
            to_debt.remaining_debt -= difference
            if to_debt.remaining_debt <= 0:
                to_debt.is_paid = True
            else:
                to_debt.is_paid = False
            to_debt.save()
        return super().update(instance, validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        to_debt = attrs.get('to_debt')

        if to_debt and to_debt.is_paid:
            raise ValidationError({'to_debt': 'not found'})

        from_user = attrs.get('from_user')
        if from_user and user.director_id != from_user.director_id:
            raise ValidationError({'from_user': 'not found'})
        return attrs


class DirectorManagerDebtRepayFromPharmacySerializer(DebtRepayFromPharmacySerializer):
    class Meta:
        model = DebtRepayFromPharmacy
        fields = '__all__'
        read_only_fields = ['creator']

    def validate(self, attrs):
        user = self.context['request'].user
        to_debt = attrs.get('to_debt')
        if to_debt and to_debt.to_pharmacy.director_id != user.director_id:
            raise ValidationError({'to_pharmacy': 'not found'})
        return super().validate(attrs)


class WorkerDebtRepayFromPharmacySerializer(DebtRepayFromPharmacySerializer):
    class Meta:
        model = DebtRepayFromPharmacy
        fields = '__all__'
        read_only_fields = ('shift', 'report_date', 'creator')

    def validate(self, attrs):
        user = self.context['request'].user
        to_debt = attrs.get('to_debt')
        if to_debt and user.pharmacy_id != to_debt.to_pharmacy_id:  # last
            raise ValidationError({'to_debt': ['not found']})
        return super().validate(attrs)
