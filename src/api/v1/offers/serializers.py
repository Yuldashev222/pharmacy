from rest_framework import serializers

from .models import Offer


class OfferCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['title', 'text']


class OfferUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = ['answer_text']


class OfferRetrieveSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    creator_phone_number = serializers.CharField(source='creator.phone_number')
    creator_name = serializers.StringRelatedField(source='creator')
    creator_role = serializers.CharField(source='creator.get_role_display')

    class Meta:
        model = Offer
        fields = '__all__'
