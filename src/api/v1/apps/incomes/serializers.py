from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import PharmacyIncome


class DirectorManagerPharmacyIncomeSerializer(serializers.ModelSerializer):
    creator_name = serializers.StringRelatedField(source='creator', read_only=True)
    to_pharmacy_name = serializers.StringRelatedField(source='to_pharmacy', read_only=True)
    to_user_name = serializers.StringRelatedField(source='to_user', read_only=True)
    transfer_type_name = serializers.StringRelatedField(source='transfer_type', read_only=True)
    expense_type_name = serializers.StringRelatedField(source='expense_type', read_only=True)

    class Meta:
        model = PharmacyIncome
        fields = '__all__'
        read_only_fields = ['creator']

    def validate(self, attrs):
        user = self.context['request'].user
        to_user = attrs.get('to_user')

        if to_user and to_user.director_id != user.director_id:
            raise ValidationError({'to_user': 'not found'})

        return attrs


class WorkerPharmacyIncomeSerializer(DirectorManagerPharmacyIncomeSerializer):
    class Meta(DirectorManagerPharmacyIncomeSerializer.Meta):
        read_only_fields = ('shift', 'to_pharmacy', 'report_date', 'creator')
