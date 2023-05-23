from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import Receipt
from .serializers import ReceiptReportSerializer


class ReceiptReportAPIViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'pharmacy']
    serializer_class = ReceiptReportSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Receipt.objects.filter(creator__director_id=user.director_id)
        return queryset
