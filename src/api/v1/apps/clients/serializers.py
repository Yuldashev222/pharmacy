from rest_framework import serializers

from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Client
        fields = '__all__'
