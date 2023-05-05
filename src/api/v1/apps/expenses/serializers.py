from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from api.v1.apps.reports.models import Report

from .models import PharmacyExpense, PharmacyExpenseHistory


class PharmacyExpenseSerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='pharmacy_expense-detail', read_only=True)
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    report_date = serializers.StringRelatedField(source='report', read_only=True)
    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)  # last
    to_user_name = serializers.StringRelatedField(source='to_user', read_only=True)
    to_user_detail = serializers.HyperlinkedRelatedField(source='to_user',
                                                         view_name='user-detail', read_only=True)
    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    from_pharmacy_detail = serializers.HyperlinkedRelatedField(source='from_pharmacy',
                                                               view_name='pharmacy-detail', read_only=True)

    def update(self, instance, validated_data):
        if validated_data:
            PharmacyExpenseHistory.objects.create(
                price=instance.price,
                report_id=instance.report_id,
                shift=instance.shift,
                desc=instance.desc,
                from_pharmacy_id=instance.from_pharmacy_id,
                transfer_type=instance.transfer_type,
                pharmacy_expense_id=instance.pk,
                creator_id=self.context['request'].user.id
            )
        return super().update(instance, validated_data)

    def validate(self, attrs):
        to_user = attrs['to_user']
        transfer_type = attrs.get('transfer_type')
        user = self.context['request'].user
        if to_user:
            if to_user.is_director():
                if user.company not in to_user.companies.all():
                    raise ValidationError({'to_user': 'not found'})
            elif user.company_id != to_user.company_id:
                raise ValidationError({'to_user': 'not found'})

        if transfer_type:
            if user.is_director():
                if transfer_type.company not in user.companies.all():
                    raise ValidationError({'transfer_type': 'not found'})
            elif transfer_type.company_id != user.company_id:
                raise ValidationError({'transfer_type': 'not found'})
        return attrs


class WorkerPharmacyExpenseSerializer(PharmacyExpenseSerializer):
    class Meta:
        model = PharmacyExpense
        exclude = ('from_pharmacy', 'report')
        read_only_fields = ('shift',)
        extra_kwargs = {
            'to_user': {'write_only': True},
        }


class DirectorManagerPharmacyExpenseSerializer(PharmacyExpenseSerializer):
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    def create(self, validated_data):
        if not validated_data.get('report'):
            raise ValidationError({'r_date': 'This field is required.'})
        return super().create(validated_data)

    class Meta:
        model = PharmacyExpense
        exclude = ('report',)
        extra_kwargs = {
            'from_pharmacy': {'required': True, 'write_only': True},
            'to_user': {'write_only': True},
        }

    def validate(self, attrs):
        user = self.context['request'].user
        if user.is_director():
            if attrs['from_pharmacy'] not in user.director_pharmacies_all():
                raise ValidationError({'from_pharmacy': 'not found'})
        elif attrs['from_pharmacy'] not in user.manager_pharmacies_all():
            raise ValidationError({'from_pharmacy': 'not found'})

        if attrs.get('r_date'):
            attrs['report'] = Report.objects.get_or_create(report_date=attrs['r_date'])[0]
            del attrs['r_date']
        return super().validate(attrs)


class PharmacyExpenseHistorySerializer(serializers.ModelSerializer):
    updated_at = serializers.DateTimeField(source='created_at')
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='pharmacy_expense_history-detail', read_only=True)
    updater_name = serializers.StringRelatedField(source='creator', read_only=True)
    updater_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    report_date = serializers.StringRelatedField(source='report', read_only=True)
    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)  # last
    pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    pharmacy_detail = serializers.HyperlinkedRelatedField(source='from_pharmacy',
                                                          view_name='pharmacy-detail', read_only=True)
    pharmacy_expense_name = serializers.StringRelatedField(source='pharmacy_expense', read_only=True)
    pharmacy_expense_detail = serializers.HyperlinkedRelatedField(source='pharmacy_expense',
                                                                  view_name='pharmacy_expense-detail', read_only=True)

    class Meta:
        model = PharmacyExpenseHistory
        exclude = ('created_at', 'creator', 'report', 'pharmacy_expense', 'from_pharmacy')
