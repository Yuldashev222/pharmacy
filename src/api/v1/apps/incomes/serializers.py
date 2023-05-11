from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from api.v1.apps.reports.models import Report
from api.v1.apps.general.models import TransferMoneyType

from .models import PharmacyIncome #, PharmacyIncomeHistory


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
    to_user_name = serializers.StringRelatedField(source='to_user', read_only=True)
    to_user_detail = serializers.HyperlinkedRelatedField(source='to_user', view_name='user-detail', read_only=True)

    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    transfer_type_detail = serializers.HyperlinkedRelatedField(source='transfer_type',
                                                               view_name='transfer_type-detail', read_only=True)

    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)
    expense_type_detail = serializers.HyperlinkedRelatedField(source='expense_type',
                                                              view_name='expense_type-detail', read_only=True)

#    def update(self, instance, validated_data):
#        if validated_data:
#            PharmacyIncomeHistory.objects.create(
#                price=instance.price,
#                report_id=instance.report_id,
#                shift=instance.shift,
#                desc=instance.desc,
#                to_pharmacy=instance.to_pharmacy,
#                to_user=instance.to_user,
#                transfer_type=instance.transfer_type,
#                pharmacy_income_id=instance.pk,
#                creator_id=self.context['request'].user.id
#            )
#        return super().update(instance, validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        to_user = attrs.get('to_user')

        if to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})

        return attrs


class WorkerPharmacyIncomeSerializer(PharmacyIncomeSerializer):
    class Meta:
        model = PharmacyIncome
        exclude = ('report',)
        read_only_fields = ('shift', 'to_pharmacy')
        extra_kwargs = {}


class DirectorManagerPharmacyIncomeSerializer(PharmacyIncomeSerializer):
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    class Meta:
        model = PharmacyIncome
        exclude = ('report',)
        extra_kwargs = {
            'to_pharmacy': {'write_only': True}
        }


    def create(self, validated_data):
        if not validated_data.get('report'):
            raise ValidationError({'r_date': 'This field is required.'})
        return super().create(validated_data)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs.get('r_date'):
            attrs['report'] = Report.objects.get_or_create(report_date=attrs['r_date'])[0]
            del attrs['r_date']
        return attrs


#class PharmacyIncomeHistorySerializer(serializers.ModelSerializer):
#    updated_at = serializers.DateTimeField(source='created_at')
#    detail = serializers.HyperlinkedRelatedField(source='pk',
#                                                 view_name='pharmacy_income_history-detail', read_only=True)
#    updater_name = serializers.StringRelatedField(source='creator', read_only=True)
#    updater_detail = serializers.HyperlinkedRelatedField(source='creator',
#                                                         view_name='user-detail', read_only=True)
#    report_date = serializers.StringRelatedField(source='report', read_only=True)
#    # report_detail = serializers.HyperlinkedRelatedField(source='report',
#    #                                                     view_name='report-detail', read_only=True)  # last
#    pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
#    pharmacy_detail = serializers.HyperlinkedRelatedField(source='to_pharmacy',
#                                                          view_name='pharmacy-detail', read_only=True)
#    pharmacy_income_name = serializers.StringRelatedField(source='pharmacy_income', read_only=True)
#    pharmacy_income_detail = serializers.HyperlinkedRelatedField(source='pharmacy_income',
#                                                                 view_name='pharmacy_income-detail', read_only=True)
#
#    class Meta:
#        model = PharmacyIncomeHistory
#        exclude = ('created_at', 'creator', 'report', 'pharmacy_income', 'to_pharmacy')
