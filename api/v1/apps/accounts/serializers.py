from rest_framework import serializers

from .models import CustomUser


class UserReadOnlySerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='get_role_display')

    class Meta:
        model = CustomUser
        fields = [
            'photo', 'is_active', 'phone_number', 'email', 'first_name', 'last_name',
            'date_joined', 'role', 'shift', 'creator', 'bio', 'address'
        ]
