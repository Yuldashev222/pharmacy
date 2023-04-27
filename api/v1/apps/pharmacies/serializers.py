from rest_framework import serializers

from .models import Pharmacy


class PharmacySerializer(serializers.ModelSerializer):
    director_phone_number = serializers.CharField(source='director.phone_number', read_only=True)
    director_email = serializers.CharField(source='director.email', read_only=True)
    director_first_name = serializers.CharField(source='director.first_name', read_only=True)
    director_last_name = serializers.CharField(source='director.last_name', read_only=True)
    director_detail = serializers.HyperlinkedRelatedField(source='director', view_name='customuser-detail',
                                                          read_only=True)
    detail = serializers.HyperlinkedRelatedField(source='id', view_name='pharmacies-detail', read_only=True)

    class Meta:
        model = Pharmacy
        fields = '__all__'
