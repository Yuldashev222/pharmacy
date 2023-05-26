from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated
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
    serializer_class = PharmacyIncomeReportDaySerializer
    filterset_fields = {
        'report_date': ['year', 'month'],
        'pharmacy': ['exact'],
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = {
            'total_price_year': 0,
            'results': serializer.data
        }
        return Response(data)

    def get_queryset(self):
        user = self.request.user
        queryset = PharmacyIncomeReportDay.objects.filter(director_id=user.director_id)
        return queryset.order_by('report_date')
