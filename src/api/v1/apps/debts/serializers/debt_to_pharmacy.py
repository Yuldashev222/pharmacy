from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from ..models import DebtToPharmacy


class DebtToPharmacySerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    to_pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)

    def update(self, instance, validated_data):
        new_price = validated_data.get('price')
        if new_price and instance.price != new_price:
            instance.remaining_debt += new_price - instance.price
            if instance.remaining_debt <= 0:
                instance.is_paid = True
            else:
                instance.is_paid = False
        return super().update(instance, validated_data)


class DirectorManagerDebtToPharmacySerializer(DebtToPharmacySerializer):
    class Meta:
        model = DebtToPharmacy
        fields = '__all__'
        read_only_fields = ('is_paid', 'remaining_debt')

    def validate(self, attrs):
        user = self.context['request'].user
        if attrs['to_pharmacy'].director_id != user.director_id:
            raise ValidationError({'to_pharmacy': 'not found'})
        return attrs


class WorkerDebtToPharmacySerializer(DebtToPharmacySerializer):
    class Meta:
        model = DebtToPharmacy
        fields = '__all__'
        read_only_fields = ('is_paid', 'report_date', 'to_pharmacy', 'shift', 'remaining_debt')
