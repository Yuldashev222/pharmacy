from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..models import UserExpense


class UserExpenseSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    from_user_name = serializers.StringRelatedField(source='from_user', read_only=True)
    to_user_name = serializers.StringRelatedField(source='to_user', read_only=True)
    to_pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)


class WorkerUserExpenseSerializer(UserExpenseSerializer):
    class Meta:
        model = UserExpense
        fields = '__all__'
        read_only_fields = ('shift', 'to_pharmacy', 'report_date')

    def validate(self, attrs):
        user = self.context['request'].user
        from_user = attrs['from_user']
        to_user = attrs.get('to_user')

        if from_user.director_id != user.director_id:
            raise ValidationError({'from_user': 'not found'})

        if not to_user:
            attrs['to_pharmacy'] = user.pharmacy
        elif to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})
        return super().validate(attrs)


class DirectorManagerUserExpenseSerializer(UserExpenseSerializer):
    class Meta:
        model = UserExpense
        fields = '__all__'

    def validate(self, attrs):
        user = self.context['request'].user
        from_user = attrs['from_user']
        to_user = attrs.get('to_user')
        to_pharmacy = attrs.get('to_pharmacy')

        if user.director_id != from_user.director_id:
            raise ValidationError({'from_user': 'not found'})

        if not (to_user or to_pharmacy):
            raise ValidationError('to_user or to_pharmacy field is required.')

        if to_user and to_pharmacy:
            raise ValidationError('select one of the two fields. (to_user or to_pharmacy )')

        if to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})

        if to_pharmacy and to_pharmacy.director_id != user.director_id:
            raise ValidationError({'to_pharmacy': 'not found'})

        return super().validate(attrs)
