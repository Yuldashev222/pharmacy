from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.v1.apps.accounts.permissions import IsDirector, IsManager
from api.v1.apps.pharmacies.models import Check


class CheckReportSerializer(serializers.Serializer):
    report_date = serializers.DateField()
    price = serializers.IntegerField()
    total_amount = serializers.SerializerMethodField()

    def get_total_amount(self):
        return 


class CheckReportAPIViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'pharmacy']
    serializer_class = CheckReportSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Check.objects.filter(creator__director_id=user.director_id)
        return queryset
