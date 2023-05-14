from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from ..models import DebtFromPharmacy


class DebtFromPharmacySerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='debt_from_pharmacy-detail', read_only=True)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    from_pharmacy_detail = serializers.HyperlinkedRelatedField(source='from_pharmacy',
                                                               view_name='pharmacy-detail', read_only=True)
    repaid_debt = serializers.FloatField(read_only=True)

    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    transfer_type_detail = serializers.HyperlinkedRelatedField(source='transfer_type',
                                                               view_name='transfer_type-detail', read_only=True)

    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)
    expense_type_detail = serializers.HyperlinkedRelatedField(source='expense_type',
                                                              view_name='expense_type-detail', read_only=True)

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
    class Meta(DebtFromPharmacySerializer.Meta):
        read_only_fields = ('is_paid', 'shift', 'from_pharmacy', 'remaining_debt')

    def validate(self, attrs):
        user = self.context['request'].user
        attrs['report_date'] = date.today()
        attrs['from_pharmacy'] = user.pharmacy
        attrs['shift'] = user.shift
        return attrs


class DirectorManagerDebtFromPharmacySerializer(DebtFromPharmacySerializer):
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    def create(self, validated_data):
        if not validated_data.get('report_date'):
            raise ValidationError({'report_date': 'required'})
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user

        if attrs['from_pharmacy'].director_id != user.director_id:
            ValidationError({'from_pharmacy': 'not found'})
        return attrs
