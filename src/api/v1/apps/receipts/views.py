from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.pharmacies.services import get_worker_report_date
from api.v1.apps.accounts.permissions import NotProjectOwner

from .models import Receipt
from .serializers import WorkerReceiptCreateUpdateSerializer, DirectorManagerReceiptCreateUpdateSerializer


class ReceiptCreateUpdateAPIView(ModelViewSet):
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
            data['report_date'] = get_worker_report_date(user.pharmacy.last_shift_end_hour)
            data['shift'] = user.shift
            data['pharmacy_id'] = user.pharmacy_id
        serializer.save(**data)

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = Receipt.objects.filter(shift=user.shift,
                                              pharmacy_id=user.pharmacy_id,
                                              report_date=get_worker_report_date(user.pharmacy.last_shift_end_hour))

        else:
            queryset = Receipt.objects.filter(creator__director_id=user.director_id)
        return queryset
