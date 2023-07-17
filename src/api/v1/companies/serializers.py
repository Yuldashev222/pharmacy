from rest_framework import serializers

from .models import Company, TransferMoneyType


class TransferMoneyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferMoneyType
        exclude = ('director',)


class CompanySerializer(serializers.ModelSerializer):
    director_name = serializers.StringRelatedField(source='director', read_only=True)

    class Meta:
        model = Company
        fields = '__all__'
        read_only_fields = ('director',)
