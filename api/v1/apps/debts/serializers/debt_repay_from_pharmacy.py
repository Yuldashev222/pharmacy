from datetime import date

from django.core.validators import MaxValueValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.v1.apps.accounts.enums import UserRole
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


class DirectorManagerDebtRepayFromPharmacySerializer(DebtRepayFromPharmacySerializer):
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])
    report = serializers.HiddenField(default=1)

    class Meta:
        model = DebtRepayFromPharmacy
        fields = '__all__'
        extra_kwargs = {
            'to_debt': {'write_only': True},
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
            if attrs['to_debt'].to_pharmacy not in user.director_pharmacies_all():
                raise ValidationError({'to_pharmacy': 'not found'})
        else:
            if attrs['to_debt'].to_pharmacy not in user.manager_pharmacies_all():
                raise ValidationError({'to_pharmacy': 'not found'})
        return attrs


class WorkerDebtRepayFromPharmacySerializer(DebtRepayFromPharmacySerializer):
    class Meta:
        model = DebtRepayFromPharmacy
        fields = '__all__'
        read_only_fields = ('report',)
        extra_kwargs = {
            'to_debt': {'write_only': True},
        }

    def validate(self, attrs):
        user = self.context['request'].user
        if user.pharmacy_id != attrs['to_debt'].to_pharmacy_id:
            raise ValidationError({'to_debt': ['not found']})
        attrs['report'] = Report.objects.get_or_create(report_date=date.today())[0]
        attrs['shift'] = user.shift
        return attrs
