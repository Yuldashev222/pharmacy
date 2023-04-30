from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Pharmacy


class PharmacySerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='id',
                                                 view_name='pharmacy-detail',
                                                 read_only=True)
    company_detail = serializers.HyperlinkedRelatedField(source='company',
                                                         view_name='company-detail',
                                                         read_only=True)

    def validate_company(self, obj):
        if obj not in self.context['request'].user.companies.all():
            raise ValidationError('not found')
        return obj

    class Meta:
        model = Pharmacy
        fields = '__all__'

    def update(self, instance, validated_data):
        if validated_data.get('company'):
            del validated_data['company']
        return super().update(instance, validated_data)
