from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
        extra_kwargs = {
            'company': {'required': False, 'allow_null': True}
        }

    def validate(self, attrs):
        user = self.context['request'].user
        if user.is_director():
            if not attrs.get('company'):
                raise ValidationError({'company': 'This field is required.'})
            if attrs['company'] not in user.companies.all():
                raise ValidationError({'company': 'not found'})
        else:
            attrs['company'] = user.company
        return attrs
