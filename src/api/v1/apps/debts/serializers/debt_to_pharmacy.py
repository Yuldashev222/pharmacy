from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from api.v1.apps.reports.models import Report

from ..models import DebtToPharmacy


class DebtToPharmacySerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='debt_to_pharmacy-detail', read_only=True)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    report_date = serializers.StringRelatedField(source='report', read_only=True)
    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)  # last
    to_pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    to_pharmacy_detail = serializers.HyperlinkedRelatedField(source='to_pharmacy',
                                                             view_name='pharmacy-detail', read_only=True)
    repaid_debt = serializers.FloatField(read_only=True)

    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    transfer_type_detail = serializers.HyperlinkedRelatedField(source='transfer_type',
                                                               view_name='transfer_type-detail', read_only=True)

    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)
    expense_type_detail = serializers.HyperlinkedRelatedField(source='expense_type',
                                                              view_name='expense_type-detail', read_only=True)


class DirectorManagerDebtToPharmacySerializer(DebtToPharmacySerializer):
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    class Meta:
        model = DebtToPharmacy
        exclude = ('report',)
        read_only_fields = ('is_paid',)

    def create(self, validated_data):
        if not validated_data.get('report'):
            raise ValidationError({'r_date': 'required'})
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        if attrs['to_pharmacy'].director_id != user.director_id:
            raise ValidationError({'to_pharmacy': 'not found'})

        r_date = attrs.get('r_date')
        if r_date:
            attrs['report'] = Report.objects.get_or_create(report_date=r_date)[0]
            del r_date
        return attrs


class WorkerDebtToPharmacySerializer(DebtToPharmacySerializer):
    class Meta:
        model = DebtToPharmacy
        fields = '__all__'
        read_only_fields = ('is_paid', 'report', 'to_pharmacy', 'shift')

    def validate(self, attrs):
        user = self.context['request'].user
        attrs['report'] = Report.objects.get_or_create(report_date=date.today())[0]
        attrs['to_pharmacy'] = user.pharmacy
        attrs['shift'] = user.shift
        return attrs
