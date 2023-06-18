from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Pharmacy


class PharmacySerializer(serializers.ModelSerializer):
    director_name = serializers.StringRelatedField(source='director', read_only=True)

    class Meta:
        model = Pharmacy
        exclude = ('director',)

    def create(self, validated_data):
        director = validated_data['director']
        name = validated_data['name']
        if Pharmacy.objects.filter(name=name, director_id=director.id).exists():
            raise ValidationError({'name': 'unique'})
        return super().create(validated_data)