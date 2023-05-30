from datetime import date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from .models import Receipt
from .serializers import WorkerReceiptCreateUpdateSerializer, DirectorManagerReceiptCreateUpdateSerializer


class ReceiptCreateUpdateAPIView(CreateModelMixin,
                                 UpdateModelMixin,
                                 GenericViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'pharmacy']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return WorkerReceiptCreateUpdateSerializer
        return DirectorManagerReceiptCreateUpdateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(report_date=date.today(), shift=user.shift, pharmacy_id=user.pharmacy_id)
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = Receipt.objects.filter(report_date=date.today(), shift=user.shift, pharmacy_id=user.pharmacy_id)
        else:
            queryset = Receipt.objects.filter(creator__director_id=user.director_id)
        return queryset
