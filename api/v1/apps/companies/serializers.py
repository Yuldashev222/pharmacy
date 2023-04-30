from rest_framework import serializers

from .models import Company


class CompanySerializer(serializers.ModelSerializer):
    detail = serializers.HyperlinkedRelatedField(source='pk',
                                                 view_name='company-detail',
                                                 read_only=True)

    class Meta:
        model = Company
        exclude = ['director']
