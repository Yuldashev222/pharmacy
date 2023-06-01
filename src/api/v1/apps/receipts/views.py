from datetime import date
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import UpdateModelMixin, CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from api.v1.apps.accounts.permissions import NotProjectOwner

from .models import Receipt
from .serializers import WorkerReceiptCreateUpdateSerializer, DirectorManagerReceiptCreateUpdateSerializer


class ReceiptCreateUpdateAPIView(CreateModelMixin,
                                 UpdateModelMixin,
                                 GenericViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'pharmacy']
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return WorkerReceiptCreateUpdateSerializer
        return DirectorManagerReceiptCreateUpdateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        data = {'creator_id': user.id}
        if user.is_worker:
            data['report_date'] = date.today()
            data['shift'] = user.shift
            data['pharmacy_id'] = user.pharmacy_id
        serializer.save(**data)

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = Receipt.objects.filter(report_date=date.today(), shift=user.shift, pharmacy_id=user.pharmacy_id)
        else:
            queryset = Receipt.objects.filter(creator__director_id=user.director_id)
        return queryset
