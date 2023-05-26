from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import PharmacyIncomeReportMonth, PharmacyIncomeReportDay


class PharmacyIncomeReportMonthSerializer(ModelSerializer):
    class Meta:
        model = PharmacyIncomeReportMonth
        fields = ['month', 'price', 'receipt_price']


class PharmacyIncomeReportDaySerializer(ModelSerializer):
    class Meta:
        model = PharmacyIncomeReportDay
        fields = ['report_date', 'receipt_price', 'price']


class PharmacyIncomeReportMonthAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    serializer_class = PharmacyIncomeReportMonthSerializer
    filterset_fields = ['year', 'pharmacy']

    def get_queryset(self):
        user = self.request.user
        queryset = PharmacyIncomeReportMonth.objects.filter(director_id=user.director_id)
        return queryset.order_by('month')


class PharmacyIncomeReportDayAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    serializer_class = PharmacyIncomeReportDaySerializer
    filterset_fields = {
        'report_date': ['year', 'month'],
        'pharmacy': ['exact'],
    }

    def get_queryset(self):
        user = self.request.user
        queryset = PharmacyIncomeReportDay.objects.filter(director_id=user.director_id)
        return queryset.order_by('report_date')
