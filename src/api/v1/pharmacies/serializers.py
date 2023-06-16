from rest_framework import serializers

from .models import Pharmacy


class PharmacySerializer(serializers.ModelSerializer):
    director_name = serializers.StringRelatedField(source='director', read_only=True)

    class Meta:
        model = Pharmacy
        exclude = ('director',)
