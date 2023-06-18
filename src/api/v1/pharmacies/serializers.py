from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Pharmacy


class PharmacySerializer(serializers.ModelSerializer):
    director_name = serializers.StringRelatedField(source='director', read_only=True)

    class Meta:
        model = Pharmacy
        exclude = ('director',)

    def create(self, validated_data):
        director_id = validated_data['director_id']
        name = validated_data['name']
        if Pharmacy.objects.filter(name=name, director_id=director_id).exists():
            raise ValidationError({'name': 'unique'})
        return super().create(validated_data)
