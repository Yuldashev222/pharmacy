from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Firm, FirmIncome, FirmFromDebtExpense, FirmFromPharmacyExpense


class FirmSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    director_name = serializers.StringRelatedField(source='director', read_only=True)

    class Meta:
        model = Firm
        exclude = ('director',)


class FirmIncomeSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    to_pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    from_firm_name = serializers.StringRelatedField(source='from_firm', read_only=True)

    class Meta:
        model = FirmIncome
        fields = '__all__'
        read_only_fields = ('paid_on_time', 'is_paid')

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
    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    to_firm_name = serializers.StringRelatedField(source='to_firm', read_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if attrs['to_firm'].director_id != user.director_id:
            raise ValidationError({'to_firm': 'not found'})
        return attrs


class FirmFromPharmacyExpenseSerializer(FirmExpenseSerializer):
    from_user_name = serializers.StringRelatedField(source='from_user', read_only=True)

    class Meta:
        model = FirmFromPharmacyExpense
        exclude = ('verified_code',)
        read_only_fields = ('is_verified',)

    def validate(self, attrs):
        user = self.context['request'].user
        from_user = attrs.get('from_user')

        if from_user and user.director_id != from_user.director_id:
            raise ValidationError({'from_user': 'not found'})

        return super().validate(attrs)


class WorkerFirmFromPharmacyExpenseSerializer(FirmFromPharmacyExpenseSerializer):
    class Meta(FirmFromPharmacyExpenseSerializer.Meta):
        read_only_fields = ('report_date', 'shift', 'from_pharmacy')


class DirectorManagerFirmFromPharmacyExpenseSerializer(FirmFromPharmacyExpenseSerializer):
    def validate(self, attrs):
        user = self.context['request'].user
        from_pharmacy = attrs['from_pharmacy']

        if from_pharmacy and user.director_id != from_pharmacy.director_id:
            raise ValidationError({'from_pharmacy': 'not found'})

        return super().validate(attrs)


class FirmFromDebtExpenseSerializer(FirmExpenseSerializer):
    creator = None
    from_debt_name = serializers.StringRelatedField(source='from_debt', read_only=True)
    creator_name = serializers.StringRelatedField(source='from_debt.creator', read_only=True)
    created_at = serializers.DateTimeField(source='from_debt.created_at', format='%Y-%m-%d', read_only=True)
    from_pharmacy_name = serializers.StringRelatedField(source='from_debt.to_pharmacy', read_only=True)
    to_firm_name = serializers.StringRelatedField(source='to_firm', read_only=True)

    class Meta:
        model = FirmFromDebtExpense
        exclude = ('verified_code',)
        # fields = '__all__'
        read_only_fields = ('is_verified',)

    def validate(self, attrs):
        user = self.context['request'].user
        from_debt = attrs['from_debt']

        if user.is_worker:
            if user.pharmacy_id != from_debt.to_pharmacy_id:
                raise ValidationError({'from_debt': 'not found'})
        elif user.director_id != from_debt.creator.director_id:
            raise ValidationError({'from_debt': 'not found'})

        return super().validate(attrs)


class FirmExpenseVerifySerializer(serializers.Serializer):
    code = serializers.IntegerField()
    is_from_debt = serializers.BooleanField()
    firm_expense_id = serializers.IntegerField()

    def validate(self, attrs):
        code = attrs['code']
        firm_expense_id = attrs['firm_expense_id']
        is_from_debt = attrs['is_from_debt']
        try:
            if is_from_debt:
                firm_expense = FirmFromDebtExpense.objects.get(pk=firm_expense_id, is_verified=False)
            else:
                firm_expense = FirmFromPharmacyExpense.objects.get(pk=firm_expense_id, is_verified=False)
        except (FirmFromDebtExpense.DoesNotExist, FirmFromPharmacyExpense.DoesNotExist):
            raise ValidationError({'firm_expense_id': 'not found'})
        if firm_expense.verified_code != code:
            firm_expense.delete()
            raise ValidationError({'code': 'Not Valid'})

        firm_expense.is_verified = True
        firm_expense.save()
        return attrs
