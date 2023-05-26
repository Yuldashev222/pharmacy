from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import AllReturnProductReportMonth


class AllReturnProductReportMonthSerializer(ModelSerializer):
    class Meta:
        model = AllReturnProductReportMonth
        fields = ['month', 'price']


class AllReturnProductReportMonthAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    serializer_class = AllReturnProductReportMonthSerializer
    filterset_fields = ['year']

    def get_queryset(self):
        user = self.request.user
        queryset = AllReturnProductReportMonth.objects.filter(director_id=user.director_id)
        return queryset.order_by('month')
