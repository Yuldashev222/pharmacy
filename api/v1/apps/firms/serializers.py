from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Firm, FirmIncome


class FirmSerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='id',
                                                 view_name='firm-detail',
                                                 read_only=True)
    company_detail = serializers.HyperlinkedRelatedField(source='company',
                                                         view_name='company-detail',
                                                         read_only=True)

    def validate_company(self, obj):
        if obj not in self.context['request'].user.companies.all():
            raise ValidationError('not found')
        return obj

    class Meta:
        model = Firm
        fields = '__all__'

    def update(self, instance, validated_data):
        if validated_data.get('company'):
            del validated_data['company']
        return super().update(instance, validated_data)


class FirmIncomeSerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='id',
                                                 view_name='firm_income-detail',
                                                 read_only=True)
    firm_detail = serializers.HyperlinkedRelatedField(source='firm',
                                                      view_name='firm-detail',
                                                      read_only=True)

    def validate_from_firm(self, obj):
        if obj not in Firm.objects.filter(company__in=self.context['request'].user.companies.all()):
            raise ValidationError('not found')
        return obj

    class Meta:
        model = FirmIncome
        fields = '__all__'

    # def update(self, instance, validated_data):
    #     if validated_data.get('company'):
    #         del validated_data['company']
    #     return super().update(instance, validated_data)
