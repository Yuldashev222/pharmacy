from rest_framework import serializers
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.companies.enums import StaticEnv
from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import ReturnProductReportMonth
from ..models import PharmacyExpense


class ReturnProductSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()

    class Meta:
        model = PharmacyExpense
        fields = ['creator', 'price', 'created_at', 'report_date', 'second_name']


class ReturnProductAPIView(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    serializer_class = ReturnProductSerializer
    filterset_fields = {
        'report_date': ['year', 'month'],
        'from_pharmacy': ['exact']
    }

    def get_queryset(self):
        user = self.request.user
        queryset = PharmacyExpense.objects.filter(
            from_pharmacy__director_id=user.director_id,
            expense_type_id=StaticEnv.return_product_id.value
        )
        return queryset.order_by('-created_at')


class ReturnProductReportMonthSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()

    class Meta:
        model = ReturnProductReportMonth
        fields = ['month', 'price']


class ReturnProductReportMonthAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    serializer_class = ReturnProductReportMonthSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filterset_fields = ['year', 'pharmacy']

    def get_queryset(self):
        user = self.request.user
        queryset = ReturnProductReportMonth.objects.filter(director_id=user.director_id,)
        return queryset.order_by('month')
