from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from api.v1.apps.reports.models import Report

from ..models import DebtRepayFromPharmacy


class DebtRepayFromPharmacySerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='debt_repay_from_pharmacy-detail', read_only=True)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    report_date = serializers.StringRelatedField(source='report', read_only=True)
    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)  # last
    to_debt_name = serializers.StringRelatedField(source='to_debt', read_only=True)
    to_debt_detail = serializers.HyperlinkedRelatedField(source='to_debt',
                                                         view_name='debt_to_pharmacy-detail', read_only=True)
    from_user_name = serializers.StringRelatedField(source='from_user', read_only=True)
    from_user_detail = serializers.HyperlinkedRelatedField(source='from_user',
                                                           view_name='user-detail', read_only=True)

    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    transfer_type_detail = serializers.HyperlinkedRelatedField(source='transfer_type',
                                                               view_name='transfer_type-detail', read_only=True)

    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)
    expense_type_detail = serializers.HyperlinkedRelatedField(source='expense_type',
                                                              view_name='expense_type-detail', read_only=True)

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
        to_debt = attrs['to_debt']

        if to_debt.is_paid:
            raise ValidationError({'to_debt': 'not found'})

        from_user = attrs.get('from_user')
        if from_user:
            if user.director_id != from_user.director_id:
                raise ValidationError({'from_user': 'not found'})
        return attrs


class DirectorManagerDebtRepayFromPharmacySerializer(DebtRepayFromPharmacySerializer):
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    class Meta:
        model = DebtRepayFromPharmacy
        exclude = ('report',)

    def create(self, validated_data):
        if not validated_data.get('report'):
            raise ValidationError({'r_date': 'required'})
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user

        if attrs['to_debt'].to_pharmacy.director_id != user.director_id:
            raise ValidationError({'to_pharmacy': 'not found'})

        if attrs.get('r_date'):
            attrs['report'] = Report.objects.get_or_create(report_date=attrs['r_date'])[0]
            del attrs['r_date']
        return super().validate(attrs)


class WorkerDebtRepayFromPharmacySerializer(DebtRepayFromPharmacySerializer):
    class Meta:
        model = DebtRepayFromPharmacy
        exclude = ('report',)
        read_only_fields = ('shift',)

    def validate(self, attrs):
        user = self.context['request'].user
        if user.pharmacy_id != attrs['to_debt'].to_pharmacy_id:
            raise ValidationError({'to_debt': ['not found']})
        return super().validate(attrs)
