from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    detail = serializers.HyperlinkedRelatedField(source='id',
                                                 view_name='client-detail',
                                                 read_only=True)

    class Meta:
        model = Client
        exclude = ('director',)
