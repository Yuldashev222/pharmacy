from rest_framework import serializers
from django.core.validators import MinValueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer

from .models import CustomUser

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainSerializer


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data['user'] = UserReadOnlySerializer(self.user).data

        return data


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    token_class = RefreshToken

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data['user'] = UserReadOnlySerializer(self.user).data

        return data


class UserCreateSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'phone_number', 'password', 'email', 'first_name', 'wage',
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
        fields = UserCreateSerializer.Meta.fields + ['pharmacy', 'shift', 'is_main_worker']
        extra_kwargs = UserCreateSerializer.Meta.extra_kwargs.copy()
        extra_kwargs['pharmacy'] = {'required': True, 'allow_null': False}
        extra_kwargs['shift'] = {'required': True, 'validators': [MinValueValidator(1)]}

    def validate(self, attrs):
        is_main_worker = attrs['is_main_worker']
        shift = attrs['shift']
        pharmacy = attrs['pharmacy']

        if is_main_worker and CustomUser.objects.filter(is_main_worker=True, shift=shift,
                                                        pharmacy_id=pharmacy.id).exists():
            raise ValidationError({'is_main_worker': 'unique'})

        return super().validate(attrs)

    def validate_pharmacy(self, obj):
        user = self.context['request'].user
        if obj.director_id != user.director_id:
            raise ValidationError('not found')
        return obj


class UserReadOnlySerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)
    director = serializers.StringRelatedField(read_only=True)
    pharmacy_name = serializers.StringRelatedField(source='pharmacy', read_only=True)
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone_number', 'first_name', 'last_name', 'role', 'shift',
            'creator', 'pharmacy', 'director', 'pharmacy_name',
            'wage', 'bio', 'photo', 'address', 'email', 'is_active',
            'date_joined',
        ]


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
        fields = ['id', 'phone_number', 'is_active', 'password']
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
        fields = DirectorUpdateDestroySerializer.Meta.fields + ['shift', 'wage']


class WorkerUpdateDestroySerializer(DirectorUpdateDestroySerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'phone_number', 'is_active', 'shift', 'password', 'wage', 'is_main_worker']

    def update(self, instance, validated_data):
        is_main_worker = validated_data.get('is_main_worker')
        shift = validated_data.get('shift', instance.shift)

        if is_main_worker and is_main_worker != instance.is_main_worker:
            if CustomUser.objects.filter(is_main_worker=True, shift=shift, pharmacy_id=instance.pharmacy_id).exists():
                raise ValidationError({'is_main_worker': 'unique'})

        return super().update(instance, validated_data)


class OwnerRetrieveUpdateSerializer(serializers.ModelSerializer):
    director = serializers.StringRelatedField(read_only=True)
    pharmacy = serializers.StringRelatedField(read_only=True)
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone_number', 'first_name', 'last_name', 'role', 'shift',
            'pharmacy', 'director', 'wage', 'bio', 'photo',
            'address', 'email', 'is_active', 'date_joined', 'is_main_worker'
        ]
        read_only_fields = ['date_joined', 'is_active', 'phone_number', 'wage', 'is_main_worker', 'shift']
