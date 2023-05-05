from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from api.v1.apps.reports.models import Report
from api.v1.apps.general.models import TransferMoneyType

from .models import PharmacyIncome, PharmacyIncomeHistory


class PharmacyIncomeSerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='pharmacy_income-detail', read_only=True)
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

    class Meta:
        model = PharmacyIncome
        exclude = ('report',)
        extra_kwargs = {
            'to_pharmacy': {'write_only': True}
        }

    def update(self, instance, validated_data):
        if validated_data:
            PharmacyIncomeHistory.objects.create(
                price=instance.price,
                report_id=instance.report_id,
                shift=instance.shift,
                desc=instance.desc,
                to_pharmacy=instance.to_pharmacy,
                is_transfer=instance.is_transfer,
                transfer_type=instance.transfer_type,
                pharmacy_income_id=instance.pk,
                creator_id=self.context['request'].user.id
            )
        return super().update(instance, validated_data)

    def validate(self, attrs):
        user = self.context['request'].user

        if attrs.get('is_transfer', 'no') not in [False, 'no'] and not attrs.get('transfer_type'):
            raise ValidationError({'transfer_type': 'This field is required.'})

        transfer_type = attrs.get('transfer_type')
        if transfer_type:
            if user.is_director() \
                    and transfer_type not in TransferMoneyType.objects.filter(company__in=user.companies.all()):
                raise ValidationError({'transfer_type': 'not found'})
            elif transfer_type not in TransferMoneyType.objects.filter(company_id=user.company_id):
                raise ValidationError({'transfer_type': 'not found'})
        return attrs


class WorkerPharmacyIncomeSerializer(PharmacyIncomeSerializer):
    class Meta(PharmacyIncomeSerializer.Meta):
        exclude = ('report', 'to_pharmacy')
        read_only_fields = ('shift', 'report')
        extra_kwargs = {}

    def validate(self, attrs):
        user = self.context['request'].user
        attrs['report'] = Report.objects.get_or_create(report_date=date.today())[0]
        attrs['shift'], attrs['to_pharmacy'] = user.shift, user.pharmacy
        return super().validate(attrs)


class DirectorManagerPharmacyIncomeSerializer(PharmacyIncomeSerializer):
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    def create(self, validated_data):
        if not validated_data.get('report'):
            raise ValidationError({'r_date': 'This field is required.'})
        return super().create(validated_data)

    def validate(self, attrs):
        if attrs.get('r_date'):
            attrs['report'] = Report.objects.get_or_create(report_date=attrs['r_date'])[0]
            del attrs['r_date']
        return super().validate(attrs)


class PharmacyIncomeHistorySerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(source='created_at')
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='pharmacy_income_history-detail', read_only=True)
    updater_name = serializers.StringRelatedField(source='creator', read_only=True)
    updater_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    report_date = serializers.StringRelatedField(source='report', read_only=True)
    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)  # last
    pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    pharmacy_detail = serializers.HyperlinkedRelatedField(source='to_pharmacy',
                                                          view_name='pharmacy-detail', read_only=True)
    pharmacy_income_name = serializers.StringRelatedField(source='pharmacy_income', read_only=True)
    pharmacy_income_detail = serializers.HyperlinkedRelatedField(source='pharmacy_income',
                                                                 view_name='pharmacy_income-detail', read_only=True)

    class Meta:
        model = PharmacyIncomeHistory
        exclude = ('created_at', 'creator', 'report', 'pharmacy_income', 'to_pharmacy')
