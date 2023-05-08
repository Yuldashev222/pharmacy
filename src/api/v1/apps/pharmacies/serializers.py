from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Pharmacy


class PharmacySerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='id',
                                                 view_name='pharmacy-detail',
                                                 read_only=True)
    director_name = serializers.StringRelatedField(source='director', read_only=True)
    director_detail = serializers.HyperlinkedRelatedField(source='director',
                                                          view_name='user-detail',
                                                          read_only=True)

    class Meta:
        model = Pharmacy
        exclude = ('director',)
