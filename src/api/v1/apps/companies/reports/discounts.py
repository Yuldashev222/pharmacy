from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import AllDiscountProductReportMonth


class AllDiscountProductReportMonthSerializer(ModelSerializer):
    class Meta:
        model = AllDiscountProductReportMonth
        fields = ['month', 'price']


class AllDiscountProductReportMonthAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    serializer_class = AllDiscountProductReportMonthSerializer
    filterset_fields = ['year']

    def get_queryset(self):
        user = self.request.user
        queryset = AllDiscountProductReportMonth.objects.filter(director_id=user.director_id)
        return queryset.order_by('month')
