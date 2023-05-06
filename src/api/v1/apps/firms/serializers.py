from datetime import date

from django.core.validators import MaxValueValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.v1.apps.accounts.enums import UserRole

from .models import Firm, FirmIncome
from ..reports.models import Report


class FirmSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    detail = serializers.HyperlinkedRelatedField(source='id',
                                                 view_name='firm-detail',
                                                 read_only=True)
    company_name = serializers.StringRelatedField(source='company', read_only=True)
    company_detail = serializers.HyperlinkedRelatedField(source='company',
                                                         view_name='company-detail',
                                                         read_only=True)

    class Meta:
        model = Firm
        fields = '__all__'
        extra_kwargs = {
            'company': {'write_only': True}
        }

    def validate_company(self, obj):
        user = self.context['request'].user
        if user.is_director:
            if obj not in user.companies.all():
                raise ValidationError('not found')
        else:
            return user.company
        return obj

    def update(self, instance, validated_data):
        if validated_data.get('company'):
            del validated_data['company']
        return super().update(instance, validated_data)


class FirmIncomeSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    detail = serializers.HyperlinkedRelatedField(source='id',
                                                 view_name='firm_income-detail',
                                                 read_only=True)

    to_pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    to_pharmacy_detail = serializers.HyperlinkedRelatedField(source='to_pharmacy',
                                                             view_name='pharmacy-detail', read_only=True)
    from_firm_name = serializers.StringRelatedField(source='from_firm', read_only=True)
    from_firm_detail = serializers.HyperlinkedRelatedField(source='from_firm',
                                                           view_name='firm-detail', read_only=True)

    report_date = serializers.StringRelatedField(source='report', read_only=True)
    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)  # last
    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    class Meta:
        model = FirmIncome
        exclude = ('report',)
        read_only_fields = ('paid_on_time', 'is_paid')
        extra_kwargs = {
            'to_pharmacy': {'write_only': True},
            'from_firm': {'write_only': True},
        }

    def create(self, validated_data):
        if not validated_data.get('report'):
            raise ValidationError({'r_date': 'This field is required.'})
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user

        if user.is_director:
            if attrs['from_firm'] not in user.director_firms_all():
                raise ValidationError({'from_firm': 'not found'})
            if attrs['to_pharmacy'] not in user.director_pharmacies_all():
                raise ValidationError({'to_pharmacy': 'not found'})

        elif attrs['from_firm'] not in Firm.objects.filter(company_id=user.company_id):
            raise ValidationError({'from_firm': 'not found'})

        elif attrs['to_pharmacy'] not in user.employee_pharmacies_all():
            raise ValidationError({'to_pharmacy': 'not found'})

        if attrs.get('r_date'):
            attrs['report'] = Report.objects.get_or_create(report_date=attrs['r_date'])[0]
            del attrs['r_date']

        return attrs
