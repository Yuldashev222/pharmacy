from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import IsDirector, IsManager
from .models import PharmacyReport


class PharmacyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyReport
        exclude = [
            'expense_debt_repay_from_pharmacy',
            'expense_debt_from_pharmacy',
            'expense_pharmacy',
            'expense_firm',
        ]


class PharmacyReportAPIViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'pharmacy': ['exact'],
        'report_date': ['year', 'month'],
    }
    serializer_class = PharmacyReportSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]

    def get_queryset(self):
        user = self.request.user
        queryset = PharmacyReport.objects.filter(pharmacy__director_id=user.director_id)
        return queryset.order_by('report_date', 'shift')
