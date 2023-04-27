from rest_framework import serializers

from .models import Firm


class FirmSerializer(serializers.ModelSerializer):
    creator_phone_number = serializers.CharField(source='creator.phone_number', read_only=True)
    creator_email = serializers.CharField(source='creator.email', read_only=True)
    creator_first_name = serializers.CharField(source='creator.first_name', read_only=True)
    creator_last_name = serializers.CharField(source='creator.last_name', read_only=True)
    creator_detail = serializers.HyperlinkedRelatedField(source='creator', view_name='customuser-detail',
                                                         read_only=True)
    detail = serializers.HyperlinkedRelatedField(source='id', view_name='firm-detail', read_only=True)

    class Meta:
        model = Firm
        fields = '__all__'
