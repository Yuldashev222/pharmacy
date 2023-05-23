from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Firm, FirmIncome, FirmExpense, FirmReport
from .services import EskizUz


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
        read_only_fields = ('is_paid', 'remaining_debt')

    def validate(self, attrs):
        user = self.context['request'].user

        if attrs['from_firm'].director_id != user.director_id:
            raise ValidationError({'from_firm': 'not found'})

        if attrs['to_pharmacy'].director_id != user.director_id:
            raise ValidationError({'to_pharmacy': 'not found'})

        return attrs


class FirmIncomeUpdateSerializer(FirmIncomeSerializer):
    class Meta:
        model = FirmIncome
        fields = '__all__'
        read_only_fields = ('is_paid', 'remaining_debt', 'from_firm', 'to_pharmacy')

    def update(self, instance, validated_data):
        if validated_data:
            firm_report = FirmReport.objects.get(income_id=instance.id)
            firm_report.shift = validated_data.get('shift', instance.shift)
            firm_report.report_date = validated_data.get('report_date', instance.report_date)
            firm_report.is_transfer = validated_data.get('is_transfer_return', instance.is_transfer_return)

            new_price = validated_data.get('price')
            if new_price and instance.price != new_price:
                instance.remaining_debt += new_price - instance.price
                if instance.remaining_debt <= 0:
                    instance.is_paid = True
                else:
                    instance.is_paid = False
                firm_report.price = new_price
            firm_report.save()
        return super().update(instance, validated_data)

    def validate(self, attrs):
        return attrs


class FirmExpenseSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    to_firm_name = serializers.StringRelatedField(source='to_firm', read_only=True)
    from_user_name = serializers.StringRelatedField(source='from_user', read_only=True)
    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)

    class Meta:
        model = FirmExpense
        exclude = ('verified_code',)
        read_only_fields = ('is_verified', 'report_date', 'remaining_debt')

    def validate(self, attrs):
        user = self.context['request'].user
        from_user = attrs.get('from_user')

        if attrs['to_firm'].director_id != user.director_id:
            raise ValidationError({'to_firm': 'not found'})

        if from_user and user.director_id != from_user.director_id:
            raise ValidationError({'from_user': 'not found'})

        return attrs


class WorkerFirmExpenseSerializer(FirmExpenseSerializer):
    class Meta(FirmExpenseSerializer.Meta):
        read_only_fields = ('report_date', 'shift', 'from_pharmacy')


class DirectorManagerFirmExpenseSerializer(FirmExpenseSerializer):
    def validate(self, attrs):
        from_pharmacy = attrs['from_pharmacy']

        if from_pharmacy and self.context['request'].user.director_id != from_pharmacy.director_id:
            raise ValidationError({'from_pharmacy': 'not found'})

        return super().validate(attrs)


class FirmExpenseVerifySerializer(serializers.Serializer):
    code = serializers.IntegerField()
    firm_expense_id = serializers.IntegerField()

    def validate(self, attrs):
        code = attrs['code']
        firm_expense_id = attrs['firm_expense_id']
        try:
            firm_expense = FirmExpense.objects.get(pk=firm_expense_id, is_verified=False)
        except FirmExpense.DoesNotExist:
            raise ValidationError({'firm_expense_id': 'not found'})
        if firm_expense.verified_code != code:
            firm_expense.delete()
            raise ValidationError({'code': 'Not Valid'})

        verified_firm_worker_name = ' '.join([i for i in firm_expense.verified_firm_worker_name if i.isalpha()])

        message = EskizUz.success_message(
            firm_worker_name=verified_firm_worker_name,
            price=firm_expense.price
        )
        EskizUz.send_sms(phone_number=firm_expense.verified_phone_number[1:], message=message)

        firm_expense.is_verified = True
        firm_expense.save()
        return attrs
