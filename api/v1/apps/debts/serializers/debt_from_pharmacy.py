from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from api.v1.apps.accounts.enums import UserRole
from api.v1.apps.reports.models import Report

from ..models import DebtFromPharmacy


class DebtFromPharmacySerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='debt_from_pharmacy-detail', read_only=True)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    report_date = serializers.StringRelatedField(source='report', read_only=True)
    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)  # last
    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    from_pharmacy_detail = serializers.HyperlinkedRelatedField(source='from_pharmacy',
                                                               view_name='pharmacy-detail', read_only=True)
    repaid_debt = serializers.FloatField(read_only=True)

    class Meta:
        model = DebtFromPharmacy
        fields = '__all__'
        read_only_fields = ('is_paid', 'report')


class WorkerDebtFromPharmacySerializer(DebtFromPharmacySerializer):
    class Meta(DebtFromPharmacySerializer.Meta):
        read_only_fields = ('is_paid', 'shift', 'from_pharmacy')

    def validate(self, attrs):
        user = self.context['request'].user
        attrs['report'] = Report.objects.get_or_create(report_date=date.today())[0]
        attrs['from_pharmacy'] = user.pharmacy
        attrs['shift'] = user.shift
        return attrs


class DirectorManagerDebtFromPharmacySerializer(DebtFromPharmacySerializer):
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    def create(self, validated_data):
        if not validated_data.get('report'):
            raise ValidationError({'r_date': 'required'})
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        if user.role == UserRole.d.name:
            if attrs['from_pharmacy'] not in user.director_pharmacies_all():
                ValidationError({'from_pharmacy': 'not found'})
        elif attrs['from_pharmacy'] not in user.manager_pharmacies_all():
            ValidationError({'from_pharmacy': 'not found'})
        if attrs.get('r_date'):
            attrs['report'] = Report.objects.get_or_create(report_date=attrs['r_date'])[0]
            del attrs['r_date']
        return attrs
