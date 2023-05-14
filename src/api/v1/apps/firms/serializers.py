from datetime import date
from rest_framework import serializers
from django.core.validators import MaxValueValidator
from rest_framework.exceptions import ValidationError

from .models import Firm, FirmIncome, FirmExpense


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

    r_date = serializers.DateField(write_only=True, required=False, validators=[MaxValueValidator(date.today())])

    class Meta:
        model = FirmIncome
        exclude = ('report',)
        read_only_fields = ('paid_on_time', 'is_paid')
        extra_kwargs = {
            'to_pharmacy': {'write_only': True},
            'from_firm': {'write_only': True},
            'report_date': {'required': False},
        }

    def create(self, validated_data):
        if not validated_data.get('report_date'):
            raise ValidationError({'report_date': 'This field is required.'})
        return super().create(validated_data)

    def validate(self, attrs):
        user = self.context['request'].user

        if attrs['from_firm'].director_id != user.director_id:
            raise ValidationError({'from_firm': 'not found'})

        if attrs['to_pharmacy'].director_id != user.director_id:
            raise ValidationError({'to_pharmacy': 'not found'})

        return attrs


class FirmExpenseSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail', read_only=True)

    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    from_pharmacy_detail = serializers.HyperlinkedRelatedField(source='from_pharmacy',
                                                               view_name='pharmacy-detail', read_only=True)
    to_firm_name = serializers.StringRelatedField(source='to_firm', read_only=True)
    to_firm_detail = serializers.HyperlinkedRelatedField(source='to_firm',
                                                         view_name='firm-detail', read_only=True)

    from_debt_name = serializers.StringRelatedField(source='from_debt', read_only=True)
    from_debt_detail = serializers.HyperlinkedRelatedField(source='from_debt',
                                                           view_name='debt_to_pharmacy-detail', read_only=True)

    from_user_name = serializers.StringRelatedField(source='from_user', read_only=True)
    from_user_detail = serializers.HyperlinkedRelatedField(source='from_user',
                                                           view_name='user-detail', read_only=True)

    report_date = serializers.StringRelatedField(source='report', read_only=True)

    # report_detail = serializers.HyperlinkedRelatedField(source='report',
    #                                                     view_name='report-detail', read_only=True)  # last

    def validate(self, attrs):
        user = self.context['request'].user

        if attrs['to_firm'].director_id != user.director_id:
            raise ValidationError({'to_firm': 'not found'})

        from_debt = attrs.get('from_debt')
        from_user = attrs.get('from_user')

        if from_debt and from_user:
            raise ValidationError('from_debt or from_user enter one of the two !.')

        if from_user and from_user.director_id != user.director_id:
            raise ValidationError({'from_user': 'not found'})
        return attrs


class DirectorManagerFirmExpenseSerializer(FirmExpenseSerializer):
    class Meta:
        model = FirmExpense
        exclude = ('verified_code', 'report')
        read_only_fields = ('is_verified',)

    def validate(self, attrs):
        user = self.context['request'].user
        from_debt = attrs.get('from_debt')

        if from_debt and from_debt.to_pharmacy_id != attrs['from_pharmacy'].id:
            raise ValidationError({'from_debt': 'not found'})

        if attrs['from_pharmacy'].director_id != user.director_id:
            raise ValidationError({'from_pharmacy': 'not found'})
        return super().validate(attrs)


class WorkerFirmExpenseSerializer(FirmExpenseSerializer):
    class Meta:
        model = FirmExpense
        exclude = ('verified_code', 'report')
        read_only_fields = ('is_verified', 'from_pharmacy', 'shift')

    def validate(self, attrs):
        user = self.context['request'].user

        from_debt = attrs.get('from_debt')

        if from_debt and from_debt.to_pharmacy_id != user.pharmacy_id:
            raise ValidationError({'from_debt': 'not found'})

        return attrs


class FirmExpenseVerifySerializer(serializers.Serializer):
    code = serializers.IntegerField()
    firm_expense_id = serializers.IntegerField()

    def validate(self, attrs):
        code = attrs['code']
        firm_expense_id = attrs['firm_expense_id']
        try:
            firm_expense = FirmExpense.objects.get(pk=firm_expense_id)
        except FirmExpense.DoesNotExist:
            raise ValidationError({'firm_expense_id': 'not found'})
        print(firm_expense.verified_code)
        if firm_expense.verified_code != code:
            firm_expense.delete()
            raise ValidationError({'code': 'Not Valid'})

        firm_expense.is_verified = True
        firm_expense.save()
        return attrs

    def save(self, *args, **kwargs):
        return {'detail': 'created'}
