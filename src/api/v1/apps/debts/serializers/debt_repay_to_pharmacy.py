from datetime import date
from django.core.validators import MaxValueValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.v1.apps.accounts.enums import UserRole
from api.v1.apps.reports.models import Report

from ..models import DebtRepayToPharmacy


class DebtRepayToPharmacySerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='debt_repay_from_pharmacy-detail', read_only=True)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    report_date = serializers.StringRelatedField(source='report', read_only=True)
    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)  # last
    from_debt_name = serializers.StringRelatedField(source='from_debt', read_only=True)
    from_debt_detail = serializers.HyperlinkedRelatedField(source='from_debt',
                                                           view_name='debt_to_pharmacy-detail', read_only=True)


class DirectorManagerDebtRepayToPharmacySerializer(DebtRepayToPharmacySerializer):
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])
    report = serializers.HiddenField(default=1)

    class Meta:
        model = DebtRepayToPharmacy
        fields = '__all__'
        extra_kwargs = {
            'from_debt': {'write_only': True},
        }

    def create(self, validated_data):
        if not validated_data.get('r_date'):
            raise ValidationError({'r_date': 'required'})
        validated_data['report'] = Report.objects.get_or_create(report_date=validated_data['r_date'])[0]
        del validated_data['r_date']
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user

        if user.role == UserRole.d.name:
            if attrs['from_debt'].to_pharmacy not in user.director_pharmacies_all():
                raise ValidationError({'to_pharmacy': 'not found'})
        else:
            if attrs['from_debt'].to_pharmacy not in user.manager_pharmacies_all():
                raise ValidationError({'to_pharmacy': 'not found'})
        return attrs


class WorkerDebtRepayToPharmacySerializer(DebtRepayToPharmacySerializer):
    class Meta:
        model = DebtRepayToPharmacy
        fields = '__all__'
        read_only_fields = ('report',)
        extra_kwargs = {
            'from_debt': {'write_only': True},
        }

    def validate(self, attrs):
        user = self.context['request'].user
        if user.pharmacy_id != attrs['from_debt'].to_pharmacy_id:
            raise ValidationError({'from_debt': ['not found']})
        attrs['report'] = Report.objects.get_or_create(report_date=date.today())[0]
        attrs['shift'] = user.shift
        return attrs
