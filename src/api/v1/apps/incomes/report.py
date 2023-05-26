from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import PharmacyIncomeReportDay


class PharmacyIncomeReportDaySerializer(ModelSerializer):
    class Meta:
        model = PharmacyIncomeReportDay
        fields = ['report_date', 'receipt_price', 'price']


class PharmacyIncomeReportDayAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date__month', 'report_date__year', 'pharmacy']
    serializer_class = PharmacyIncomeReportDaySerializer

    def get_queryset(self):
        user = self.request.user
        queryset = PharmacyIncomeReportDay.objects.filter(director_id=user.director_id)
        return queryset.order_by('report_date')
