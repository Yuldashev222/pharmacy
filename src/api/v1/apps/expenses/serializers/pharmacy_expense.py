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

    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    transfer_type_detail = serializers.HyperlinkedRelatedField(source='transfer_type',
                                                               view_name='transfer_type-detail', read_only=True)

    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)
    expense_type_detail = serializers.HyperlinkedRelatedField(source='expense_type',
                                                              view_name='expense_type-detail', read_only=True)
    # expense_type = serializers.StringRelatedField(source='income_expense_type', read_only=True)
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

        if to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})

        attrs['shift'] = user.shift
        attrs['report'] = Report.objects.get_or_create(report_date=date.today())[0]
        attrs['from_pharmacy'] = user.pharmacy
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
        to_user = attrs.get('to_user')

        if from_pharmacy.director_id != user.director_id:
            raise ValidationError({'from_pharmacy': 'not found'})

        if to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})

        r_date = attrs.get('r_date')
        if r_date:
            attrs['report'] = Report.objects.get_or_create(report_date=date.today())[0]
            del attrs['r_date']
        return attrs
