from datetime import datetime, timedelta

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Firm, FirmIncome, FirmExpense, FirmReturnProduct
from .services import EskizUz


class FirmSerializer(serializers.ModelSerializer):
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    director_name = serializers.StringRelatedField(source='director', read_only=True)

    class Meta:
        model = Firm
        exclude = ('director',)
        read_only_fields = ['creator']

    def create(self, validated_data):
        director_id = validated_data['director_id']
        name = validated_data['name']
        if Firm.objects.filter(name=name, director_id=director_id).exists():
            raise ValidationError({'name': 'unique'})
        return super().create(validated_data)


class FirmIncomeSerializer(serializers.ModelSerializer):
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    from_firm_name = serializers.StringRelatedField(source='from_firm', read_only=True)

    class Meta:
        model = FirmIncome
        fields = '__all__'
        read_only_fields = ('is_paid', 'remaining_debt', 'creator')

    def validate(self, attrs):
        user = self.context['request'].user
        if attrs['from_firm'].director_id != user.director_id:
            raise ValidationError({'from_firm': 'not found'})
        return attrs


class FirmIncomeUpdateSerializer(FirmIncomeSerializer):
    class Meta:
        model = FirmIncome
        fields = '__all__'
        read_only_fields = ('is_paid', 'remaining_debt', 'from_firm', 'report_date', 'creator')

    def update(self, instance, validated_data):
        new_price = validated_data.get('price')
        if new_price and instance.price != new_price:
            instance.remaining_debt += new_price - instance.price
            if instance.remaining_debt <= 0:
                instance.is_paid = True
            else:
                instance.is_paid = False
        return super().update(instance, validated_data)

    def validate(self, attrs):
        return attrs


class FirmExpenseSerializer(serializers.ModelSerializer):
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    from_pharmacy_name = serializers.StringRelatedField(source='from_pharmacy', read_only=True)
    to_firm_name = serializers.StringRelatedField(source='to_firm', read_only=True)
    from_user_name = serializers.StringRelatedField(source='from_user', read_only=True)
    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)

    class Meta:
        model = FirmExpense
        exclude = ('verified_code',)
        extra_kwargs = {
            'from_pharmacy': {'required': True, 'allow_null': False}
        }
        # read_only_fields = ('is_verified', 'report_date', 'creator')
        read_only_fields = ('is_verified', 'creator')

    def validate(self, attrs):
        user = self.context['request'].user
        from_user = attrs.get('from_user')
        from_pharmacy_transfer = attrs.get('from_pharmacy_transfer')
        verified_phone_number = attrs.get('verified_phone_number')
        verified_firm_worker_name = attrs.get('verified_firm_worker_name')
        if not from_pharmacy_transfer and not (verified_firm_worker_name or verified_phone_number):
            raise ValidationError('error')

        if attrs['to_firm'].director_id != user.director_id:
            raise ValidationError({'to_firm': 'not found'})

        if from_user and user.director_id != from_user.director_id:
            raise ValidationError({'from_user': 'not found'})

        return attrs


class WorkerFirmExpenseSerializer(FirmExpenseSerializer):
    class Meta(FirmExpenseSerializer.Meta):
        # read_only_fields = ('report_date', 'shift', 'from_pharmacy', 'creator', 'is_verified')
        read_only_fields = ('shift', 'from_pharmacy', 'creator', 'is_verified')


class DirectorManagerFirmExpenseSerializer(FirmExpenseSerializer):
    def validate(self, attrs):
        from_pharmacy = attrs.get('from_pharmacy')
        if from_pharmacy and self.context['request'].user.director_id != from_pharmacy.director_id:
            raise ValidationError({'from_pharmacy': 'not found'})

        return super().validate(attrs)


class FirmReturnProductSerializer(serializers.ModelSerializer):
    firm_name = serializers.StringRelatedField(source='firm_income.from_firm', read_only=True)
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)

    class Meta:
        model = FirmReturnProduct
        exclude = ('verified_code',)
        read_only_fields = ('is_verified', 'report_date', 'creator')

    def validate(self, attrs):
        user = self.context['request'].user
        firm_income = attrs['firm_income']

        if attrs['price'] > firm_income.remaining_debt:
            raise ValidationError({'price': 'error'})

        if firm_income.from_firm.director_id != user.director_id:
            raise ValidationError({'firm_income': 'not found'})

        return attrs


class FirmExpenseVerifySerializer(serializers.Serializer):
    code = serializers.IntegerField()
    firm_expense_id = serializers.IntegerField()

    def validate(self, attrs):
        FirmExpense.objects.filter(is_verified=False, created_at__lt=datetime.now() - timedelta(minutes=5)).delete()

        code = attrs['code']
        firm_expense_id = attrs['firm_expense_id']
        try:
            firm_expense = FirmExpense.objects.get(pk=firm_expense_id, is_verified=False)
        except FirmExpense.DoesNotExist:
            raise ValidationError({'firm_expense_id': 'not found'})
        if firm_expense.verified_code != code:
            raise ValidationError({'code': 'Not Valid'})

        w_name = ''.join([i for i in firm_expense.verified_firm_worker_name if i.isalpha() or i in ' \''])
        message = EskizUz.success_message(firm_worker_name=w_name, price=firm_expense.price)
        EskizUz.send_sms(phone_number=firm_expense.verified_phone_number[1:], message=message)

        firm_expense.is_verified = True
        firm_expense.save()
        return attrs


class FirmReturnProductVerifySerializer(FirmExpenseVerifySerializer):
    firm_expense_id = None
    code = serializers.IntegerField()
    firm_return_id = serializers.IntegerField()

    def validate(self, attrs):
        FirmReturnProduct.objects.filter(is_verified=False, created_at__lt=datetime.now() - timedelta(minutes=5)
                                         ).delete()

        code = attrs['code']
        firm_return_id = attrs['firm_return_id']
        try:
            firm_return = FirmReturnProduct.objects.get(pk=firm_return_id, is_verified=False)
        except FirmReturnProduct.DoesNotExist:
            raise ValidationError({'firm_return_id': 'not found'})
        if firm_return.verified_code != code:
            raise ValidationError({'code': 'Not Valid'})

        w_name = ''.join([i for i in firm_return.verified_firm_worker_name if i.isalpha() or i in ' \''])
        message = EskizUz.return_product_success_message(firm_worker_name=w_name, price=firm_return.price)
        EskizUz.send_sms(phone_number=firm_return.verified_phone_number[1:], message=message)

        firm_return.is_verified = True
        firm_return.save()
        return attrs
