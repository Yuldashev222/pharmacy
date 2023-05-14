from rest_framework import serializers
from django.core.validators import MinValueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password

from .models import CustomUser


class UserCreateSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'phone_number', 'password', 'email', 'first_name',
            'last_name', 'is_active', 'photo', 'bio', 'address', 'role', 'creator'
        ]
        extra_kwargs = {
            'first_name': {'min_length': 3},
            'last_name': {'min_length': 3},
            'is_active': {'default': True},
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
                'validators': [validate_password]
            }
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class WorkerCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ['pharmacy', 'shift']
        extra_kwargs = UserCreateSerializer.Meta.extra_kwargs.copy()
        extra_kwargs['pharmacy'] = {'required': True, 'allow_null': False}
        extra_kwargs['shift'] = {'required': True, 'validators': [MinValueValidator(1)]}

    def validate_pharmacy(self, obj):
        user = self.context['request'].user
        if obj.director_id != user.director_id:
            raise ValidationError('not found')
        return obj


class UserReadOnlySerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)
    director = serializers.StringRelatedField(read_only=True)
    pharmacy = serializers.StringRelatedField(read_only=True)
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'detail', 'phone_number', 'first_name', 'last_name', 'role', 'shift',
            'creator', 'pharmacy', 'director',
            'wage', 'bio', 'photo', 'address', 'email', 'is_active',
            'date_joined',
        ]

    def get_field_names(self, declared_fields, info):
        user = self.context['request'].user
        f = super().get_field_names(declared_fields, info)
        if user.is_worker:
            return [
                'id', 'phone_number', 'first_name', 'last_name', 'role', 'shift',
                'pharmacy', 'director', 'bio', 'photo',
                'address', 'email', 'date_joined',
            ]
        return f


class RetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone_number', 'role', 'shift', 'pharmacy',
            'director', 'wage', 'is_active',
        ]

        def update(self, instance, validated_data):
            user = self.context['request'].user
            if user.is_project_owner:
                validated_data = {
                    'is_active': validated_data.get('is_active', instance.is_active),
                    'phone_number': validated_data.get('phone_number', instance.phone_number)
                }
            return super().update(instance, validated_data)


class DirectorUpdateDestroySerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone_number', 'is_active', 'password'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
                'validators': [validate_password]
            }
        }

    def validate(self, attrs):
        password = attrs.get('password')
        if password:
            attrs['password'] = make_password(password)
        return attrs


class ManagerUpdateDestroySerializer(DirectorUpdateDestroySerializer):
    class Meta(DirectorUpdateDestroySerializer.Meta):
        fields = DirectorUpdateDestroySerializer.Meta.fields + [
            'shift',
            'wage'
        ]


class WorkerUpdateDestroySerializer(DirectorUpdateDestroySerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone_number', 'is_active', 'detail', 'shift', 'password'
        ]


class OwnerRetrieveUpdateSerializer(serializers.ModelSerializer):
    director = serializers.StringRelatedField(read_only=True)
    pharmacy = serializers.StringRelatedField(read_only=True)
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'phone_number', 'first_name', 'last_name', 'role', 'shift',
            'pharmacy', 'director', 'wage', 'bio', 'photo',
            'address', 'email', 'is_active', 'date_joined',
        ]
        read_only_fields = ['date_joined', 'is_active', 'phone_number', 'wage', 'shift']
