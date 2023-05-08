from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from api.v1.apps.reports.models import Report

from .models import Firm, FirmIncome


class FirmSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)
    detail = serializers.HyperlinkedRelatedField(source='id',
                                                 view_name='firm-detail',
                                                 read_only=True)
    director_name = serializers.StringRelatedField(source='director', read_only=True)
    director_detail = serializers.HyperlinkedRelatedField(source='director',
                                                          view_name='user-detail',
                                                          read_only=True)

    class Meta:
        model = Firm
        exclude = ('director',)


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

    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)
    expense_type_detail = serializers.HyperlinkedRelatedField(source='expense_type',
                                                              view_name='expense_type-detail', read_only=True)
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

        if attrs['from_firm'].director_id != user.director_id:
            raise ValidationError({'from_firm': 'not found'})

        if attrs['to_pharmacy'].director_id != user.director_id:
            raise ValidationError({'to_pharmacy': 'not found'})

        if attrs.get('r_date'):
            attrs['report'] = Report.objects.get_or_create(report_date=attrs['r_date'])[0]
            del attrs['r_date']
        return attrs


# class FirmExpenseSerializer(serializers.ModelSerializer):
#     creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
#     creator_name = serializers.StringRelatedField(source='creator', read_only=True)
#     creator_detail = serializers.HyperlinkedRelatedField(source='creator',
#                                                          view_name='user-detail', read_only=True)
#     from_user_name = serializers.StringRelatedField(source='from_user', read_only=True)
#     from_user_detail = serializers.HyperlinkedRelatedField(source='from_user',
#                                                            view_name='user-detail', read_only=True)
#     detail = serializers.HyperlinkedRelatedField(source='id',
#                                                  view_name='firm_income-detail',
#                                                  read_only=True)
#     from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
#     from_pharmacy_detail = serializers.HyperlinkedRelatedField(source='from_pharmacy',
#                                                                view_name='pharmacy-detail', read_only=True)
#     to_firm_name = serializers.StringRelatedField(source='to_firm', read_only=True)
#     to_firm_detail = serializers.HyperlinkedRelatedField(source='to_firm',
#                                                          view_name='firm-detail', read_only=True)
#
#     report_date = serializers.StringRelatedField(source='report', read_only=True)
#     # report_detail = serializers.HyperlinkedRelatedField(source='report',
#     #                                                     view_name='report-detail', read_only=True)  # last
#     r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])
#
#     class Meta:
#         model = FirmExpense
#         exclude = ('report',)
#         read_only_fields = ('paid_on_time', 'is_paid')
#         extra_kwargs = {
#             'to_pharmacy': {'write_only': True},
#             'from_firm': {'write_only': True},
#         }
#
#     def create(self, validated_data):
#         if not validated_data.get('report'):
#             raise ValidationError({'r_date': 'This field is required.'})
#         return super().create(validated_data)
#
#     def validate(self, attrs):
#         user = self.context['request'].user
#
#         if user.is_director:
#             if attrs['from_firm'] not in user.director_firms_all():
#                 raise ValidationError({'from_firm': 'not found'})
#             if attrs['to_pharmacy'] not in user.director_pharmacies_all():
#                 raise ValidationError({'to_pharmacy': 'not found'})
#
#         elif attrs['from_firm'] not in user.employee_firms_all():
#             raise ValidationError({'from_firm': 'not found'})
#
#         elif attrs['to_pharmacy'] not in user.employee_pharmacies_all():
#             raise ValidationError({'to_pharmacy': 'not found'})
#
#         if attrs.get('r_date'):
#             attrs['report'] = Report.objects.get_or_create(report_date=attrs['r_date'])[0]
#             del attrs['r_date']
#
#         return attrs
