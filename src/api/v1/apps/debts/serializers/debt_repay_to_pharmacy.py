from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from api.v1.apps.reports.models import Report

from ..models import DebtRepayToPharmacy


class DebtRepayToPharmacySerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='debt_repay_to_pharmacy-detail', read_only=True)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    report_date = serializers.StringRelatedField(source='report', read_only=True)
    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)  # last
    from_debt_name = serializers.StringRelatedField(source='from_debt', read_only=True)
    from_debt_detail = serializers.HyperlinkedRelatedField(source='from_debt',
                                                           view_name='debt_from_pharmacy-detail', read_only=True)

    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    transfer_type_detail = serializers.HyperlinkedRelatedField(source='transfer_type',
                                                               view_name='transfer_type-detail', read_only=True)

    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)
    expense_type_detail = serializers.HyperlinkedRelatedField(source='expense_type',
                                                              view_name='expense_type-detail', read_only=True)
    is_client = serializers.BooleanField(source='from_debt.is_client', read_only=True)

    def create(self, validated_data):
        from_debt = validated_data['from_debt']
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
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    class Meta:
        model = DebtRepayToPharmacy
        exclude = ('report',)

    def create(self, validated_data):
        if not validated_data.get('report'):
            raise ValidationError({'r_date': 'required'})
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        if attrs['from_debt'].from_pharmacy.director_id != user.director_id:
            raise ValidationError({'from_pharmacy': 'not found'})

        if attrs.get('r_date'):
            attrs['report'] = Report.objects.get_or_create(report_date=attrs['r_date'])[0]
            del attrs['r_date']
        return attrs


class WorkerDebtRepayToPharmacySerializer(DebtRepayToPharmacySerializer):
    class Meta:
        model = DebtRepayToPharmacy
        fields = '__all__'
        read_only_fields = ('report', 'shift')

    def validate(self, attrs):
        user = self.context['request'].user
        if user.pharmacy_id != attrs['from_debt'].from_pharmacy_id:
            raise ValidationError({'from_debt': ['not found']})
        attrs['report'] = Report.objects.get_or_create(report_date=date.today())[0]
        attrs['shift'] = user.shift
        return attrs
