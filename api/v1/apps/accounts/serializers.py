from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework.exceptions import ValidationError

from .enums import UserRole
from .models import CustomUser


class UserCreateSerializer(serializers.ModelSerializer):
    re_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    role = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'phone_number', 'password', 're_password', 'email', 'first_name',
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
        del validated_data['re_password']
        return CustomUser.objects.create_user(**validated_data)

    def validate(self, attrs):
        if attrs['password'] != attrs['re_password']:
            raise ValidationError({'re_password': 'passwords do not match'})
        return attrs


class ManagerCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ['company']
        extra_kwargs = UserCreateSerializer.Meta.extra_kwargs.copy()
        extra_kwargs['company'] = {'allow_null': False}

    def validate(self, attrs):
        print(attrs['company'])
        user = self.context['request'].user
        if attrs['company'] not in user.companies.all():
            raise ValidationError({'company': 'not found'})
        return super().validate(attrs)


class WorkerCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = UserCreateSerializer.Meta.fields + ['pharmacy']
        extra_kwargs = UserCreateSerializer.Meta.extra_kwargs.copy()
        extra_kwargs['pharmacy'] = {'allow_null': False}

    def validate(self, attrs):
        user = self.context['request'].user
        if user.role == UserRole.d.name:
            if attrs['pharmacy'] not in user.director_pharmacies_all():
                raise ValidationError({'pharmacy': 'not found'})
        elif attrs['pharmacy'] not in user.manager_pharmacies_all():
            raise ValidationError({'pharmacy': 'not found'})
        return super().validate(attrs)


class UserReadOnlySerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField(read_only=True)
    company = serializers.StringRelatedField(read_only=True)
    pharmacy = serializers.StringRelatedField(read_only=True)
    pharmacy_detail = serializers.HyperlinkedRelatedField(source='pharmacy',
                                                          view_name='pharmacy-detail',
                                                          read_only=True)
    role = serializers.CharField(source='get_role_display', read_only=True)
    company_detail = serializers.HyperlinkedRelatedField(source='company',
                                                         view_name='company-detail',
                                                         read_only=True)
    detail = serializers.HyperlinkedRelatedField(source='id',
                                                 view_name='user-detail',
                                                 read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator',
                                                         view_name='user-detail',
                                                         read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'detail', 'phone_number', 'first_name', 'last_name', 'role', 'shift',
            'creator', 'creator_detail', 'pharmacy', 'pharmacy_detail', 'company',
            'company_detail', 'wage', 'bio', 'photo', 'address', 'email', 'is_active',
            'date_joined',
        ]

    def get_field_names(self, declared_fields, info):
        user = self.context['request'].user
        f = super().get_field_names(declared_fields, info)
        if user.role == UserRole.w.name:
            return [
                'id', 'detail', 'phone_number', 'first_name', 'last_name', 'role', 'shift',
                'pharmacy', 'pharmacy_detail', 'company', 'company_detail', 'bio', 'photo',
                'address', 'email', 'date_joined',
            ]
        return f


class RetrieveUpdateDestroySerializer(serializers.ModelSerializer):
    # company = serializers.StringRelatedField()
    # pharmacy = serializers.StringRelatedField()
    pharmacy_detail = serializers.HyperlinkedRelatedField(source='pharmacy',
                                                          view_name='pharmacy-detail',
                                                          read_only=True)
    company_detail = serializers.HyperlinkedRelatedField(source='company',
                                                         view_name='company-detail',
                                                         read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone_number', 'role', 'shift', 'pharmacy',
            'pharmacy_detail', 'company', 'company_detail', 'wage', 'is_active',
        ]

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.role == UserRole.p.name:
            validated_data = {
                'is_active': validated_data.get('is_active', instance.is_active),
                'phone_number': validated_data.get('phone_number', instance.is_active)
            }
        return super().update(instance, validated_data)


class DirectorUpdateDestroySerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='user-detail',
                                                 read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id', 'phone_number', 'is_active', 'detail',
        ]


class ManagerUpdateDestroySerializer(DirectorUpdateDestroySerializer):
    class Meta(DirectorUpdateDestroySerializer.Meta):
        fields = DirectorUpdateDestroySerializer.Meta.fields + [
            'shift',
            'wage',
        ]


class WorkerUpdateDestroySerializer(DirectorUpdateDestroySerializer):
    pass


class OwnerRetrieveUpdateSerializer(serializers.ModelSerializer):
    company = serializers.StringRelatedField(read_only=True)
    pharmacy = serializers.StringRelatedField(read_only=True)
    role = serializers.CharField(source='get_role_display', read_only=True)
    company_detail = serializers.HyperlinkedRelatedField(source='company',
                                                         view_name='company-detail',
                                                         read_only=True)
    pharmacy_detail = serializers.HyperlinkedRelatedField(source='pharmacy',
                                                          view_name='pharmacy-detail',
                                                          read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'phone_number', 'first_name', 'last_name', 'role', 'shift',
            'pharmacy', 'pharmacy_detail', 'company', 'company_detail', 'wage', 'bio', 'photo',
            'address', 'email', 'is_active', 'date_joined',
        ]
        read_only_fields = ['date_joined', 'is_active', 'phone_number', 'wage', 'shift']
