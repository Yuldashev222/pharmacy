from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import UserExpense


class UserExpenseSerializer(serializers.ModelSerializer):
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    from_user_name = serializers.StringRelatedField(source='from_user', read_only=True)
    to_user_name = serializers.StringRelatedField(source='to_user', read_only=True)
    to_pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)

    class Meta:
        extra_kwargs = {
            'from_user': {'required': True, 'allow_null': False}
        }


class WorkerUserExpenseSerializer(UserExpenseSerializer):
    class Meta(UserExpenseSerializer.Meta):
        model = UserExpense
        fields = '__all__'
        read_only_fields = ('shift', 'to_pharmacy', 'report_date', 'creator')

    def validate(self, attrs):
        user = self.context['request'].user
        from_user = attrs.get('from_user')
        to_user = attrs.get('to_user')

        if from_user and from_user.director_id != user.director_id:
            raise ValidationError({'from_user': 'not found'})

        elif to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})
        return super().validate(attrs)


class DirectorManagerUserExpenseSerializer(UserExpenseSerializer):
    class Meta(UserExpenseSerializer.Meta):
        model = UserExpense
        fields = '__all__'
        read_only_fields = ['creator']

    def validate(self, attrs):
        user = self.context['request'].user
        from_user = attrs.get('from_user')
        to_user = attrs.get('to_user')
        to_pharmacy = attrs.get('to_pharmacy')

        if from_user and user.director_id != from_user.director_id:
            raise ValidationError({'from_user': 'not found'})

        if to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})

        if to_pharmacy and to_pharmacy.director_id != user.director_id:
            raise ValidationError({'to_pharmacy': 'not found'})

        return super().validate(attrs)