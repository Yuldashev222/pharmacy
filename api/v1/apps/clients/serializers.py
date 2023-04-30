from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.v1.apps.accounts.enums import UserRole
from api.v1.apps.companies.models import Company

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    detail = serializers.HyperlinkedRelatedField(source='id',
                                                 view_name='client-detail',
                                                 read_only=True)
    company_detail = serializers.HyperlinkedRelatedField(source='company',
                                                         view_name='company-detail',
                                                         read_only=True)

    class Meta:
        model = Client
        fields = '__all__'

    def validate(self, attrs):
        user = self.context['request'].user
        if user.role == UserRole.d.name:
            if attrs['company'] not in user.companies.all():
                raise ValidationError({'company': 'not found'})
        else:
            attrs['company'] = user.company
        return attrs

    def update(self, instance, validated_data):
        if validated_data.get('company'):
            del validated_data['company']
        return super().update(instance, validated_data)
