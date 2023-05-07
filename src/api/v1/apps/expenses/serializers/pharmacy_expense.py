from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from api.v1.apps.reports.models import Report

from ..models import PharmacyExpense


class PharmacyExpenseSerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk', view_name='user_expense-detail', read_only=True)

    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator', view_name='user-detail', read_only=True)

    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    from_pharmacy_detail = serializers.HyperlinkedRelatedField(source='from_pharmacy',
                                                               view_name='user-detail', read_only=True)

    to_user_name = serializers.StringRelatedField(source='to_user', read_only=True)
    to_user_detail = serializers.HyperlinkedRelatedField(source='to_user', view_name='user-detail', read_only=True)

    to_pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    to_pharmacy_detail = serializers.HyperlinkedRelatedField(source='to_pharmacy',
                                                             view_name='pharmacy-detail', read_only=True)

    report_date = serializers.StringRelatedField(source='report', read_only=True)

    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)


class WorkerPharmacyExpenseSerializer(PharmacyExpenseSerializer):
    class Meta:
        model = PharmacyExpense
        exclude = ('report', 'from_pharmacy')
        read_only_fields = ('shift',)

    def validate(self, attrs):
        user = self.context['request'].user
        to_user = attrs.get('to_user')

        if to_user:
            if to_user.is_director:
                if user.company not in to_user.companies.all():
                    raise ValidationError({'to_user': 'not found'})
            elif to_user.company_id != user.company_id:
                raise ValidationError({'to_user': 'not found'})
        return attrs


class DirectorManagerPharmacyExpenseSerializer(PharmacyExpenseSerializer):
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    class Meta:
        model = PharmacyExpense
        exclude = ('report',)

    def create(self, validated_data):
        if not validated_data.get('report'):
            raise ValidationError({'r_date': 'This field is required.'})
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user
        from_pharmacy = attrs['from_pharmacy']

        if from_pharmacy not in user.director_pharmacies_all():
            raise ValidationError({'from_pharmacy': 'not found'})

        r_date = attrs.get('r_date')
        if r_date:
            attrs['report'] = Report.objects.get_or_create(report_date=date.today())[0]
            del attrs['r_date']
        return attrs


class DirectorPharmacyExpenseSerializer(DirectorManagerPharmacyExpenseSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.context['request'].user
        to_user = attrs.get('to_user')

        if to_user:
            if to_user.is_director:
                if user.id != to_user.id:
                    raise ValidationError({'to_user': 'not found'})
            elif to_user.company not in user.companies.all():
                raise ValidationError({'to_user': 'not found'})

        return attrs


class ManagerPharmacyExpenseSerializer(DirectorManagerPharmacyExpenseSerializer):
    def validate(self, attrs):
        attrs = super().validate(attrs)
        user = self.context['request'].user
        to_user = attrs.get('to_user')

        if to_user:
            if to_user.is_director:
                if user.id != to_user.id:
                    raise ValidationError({'to_user': 'not found'})
            elif to_user.company not in user.companies.all():
                raise ValidationError({'to_user': 'not found'})

        return attrs
