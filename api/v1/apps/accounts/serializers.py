from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError

from .enums import UserRole
from .models import CustomUser


class DirectorSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = [
            'phone_number', 'password', 're_password', 'email', 'first_name',
            'last_name', 'date_joined', 'is_active', 'photo', 'bio', 'address'
        ]
        read_only_fields = ('date_joined',)
        extra_kwargs = {
            'first_name': {'min_length': 3},
            'is_active': {'default': True},
            'last_name': {'min_length': 3},
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
                'validators': [validate_password]
            }
        }

    def create(self, validated_data):
        del validated_data['re_password']
        validated_data.update(
            {'role': UserRole.d.name, 'creator_id': self.context['request'].user.id}
        )
        return CustomUser.objects.create_user(**validated_data)

    def validate(self, attrs):
        if attrs['password'] != attrs['re_password']:
            raise ValidationError({'re_password': 'passwords do not match'})
        return attrs

    def to_representation(self, instance):
        user = self.context['request'].user
        ret = super().to_representation(instance)
        if user.role != UserRole.p.name:
            del ret['is_active'], ret['date_joined']
        return ret


class ManagerSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = CustomUser
        fields = [
            'company', 'phone_number', 'password', 're_password', 'email', 'first_name',
            'last_name', 'date_joined', 'is_active', 'photo', 'bio', 'address'
        ]
        read_only_fields = ('date_joined',)
        extra_kwargs = {
            'first_name': {'min_length': 3},
            'is_active': {'default': True},
            'last_name': {'min_length': 3},
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
                'validators': [validate_password]
            }
        }

    def create(self, validated_data):
        del validated_data['re_password']
        validated_data.update(
            {'role': UserRole.m.name, 'creator_id': self.context['request'].user.id}
        )
        return CustomUser.objects.create_user(**validated_data)

    def validate(self, attrs):
        if attrs['password'] != attrs['re_password']:
            raise ValidationError({'re_password': 'passwords do not match'})
        return attrs

    def to_representation(self, instance):
        user = self.context['request'].user
        ret = super().to_representation(instance)
        if user.role != UserRole.p.name:
            del ret['is_active'], ret['date_joined']
        return ret
