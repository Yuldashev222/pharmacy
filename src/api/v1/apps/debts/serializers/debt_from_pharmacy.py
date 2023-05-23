from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import DebtFromPharmacy


class DebtFromPharmacySerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
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

    class Meta:
        model = DebtFromPharmacy
        fields = '__all__'
        read_only_fields = ('is_paid', 'remaining_debt')


class WorkerDebtFromPharmacySerializer(DebtFromPharmacySerializer):
    class Meta:
        model = DebtFromPharmacy
        fields = '__all__'
        read_only_fields = ('is_paid', 'report_date', 'shift', 'from_pharmacy', 'remaining_debt')


class DirectorManagerDebtFromPharmacySerializer(DebtFromPharmacySerializer):
    def validate(self, attrs):
        user = self.context['request'].user
        if attrs.get('from_pharmacy') and attrs['from_pharmacy'].director_id != user.director_id:
            ValidationError({'from_pharmacy': 'not found'})
        return super().validate(attrs)
