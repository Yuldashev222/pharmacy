from rest_framework import filters
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.pharmacies.services import get_worker_report_date
from api.v1.apps.accounts.permissions import NotProjectOwner
from api.v1.apps.companies.permissions import WorkerTodayObject

from ..models import DebtFromPharmacy, DebtRepayToPharmacy
from ..serializers import debt_from_pharmacy, debt_repay_to_pharmacy


class DebtFromPharmacyAPIView(ModelViewSet):  # last
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'is_paid': ['exact'],
        'from_pharmacy': ['exact'],
        'report_date': ['exact', 'year', 'month'],
        'shift': ['exact'],
        'is_client': ['exact']
    }
    search_fields = ['to_who', 'desc']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        user = self.request.user
        if user.is_authenticated and user.is_worker and self.action not in ['list', 'retrieve']:  # last
            permission_classes += [WorkerTodayObject]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        data = {'creator_id': user.id}
        if user.is_worker:
            data['report_date'] = get_worker_report_date(user.pharmacy.last_shift_end_hour)
            data['from_pharmacy_id'] = user.pharmacy_id
            data['shift'] = user.shift
        serializer.save(**data)

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and user.is_worker:
            return debt_from_pharmacy.WorkerDebtFromPharmacySerializer
        return debt_from_pharmacy.DirectorManagerDebtFromPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy_id=user.pharmacy_id)
        else:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy__director_id=user.director_id)
        return queryset.select_related('creator', 'from_pharmacy', 'transfer_type').order_by('-created_at')


class TodayDebtFromPharmacyAPIView(DebtFromPharmacyAPIView):
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})


class DebtRepayToPharmacyAPIView(ModelViewSet):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'from_debt__is_client', 'from_debt__from_pharmacy']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        user = self.request.user
        if user.is_authenticated and user.is_worker and self.action not in ['list', 'retrieve']:
            permission_classes += [WorkerTodayObject]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        data = {'creator_id': user.id}
        if user.is_worker:
            data['report_date'] = get_worker_report_date(user.pharmacy.last_shift_end_hour)
            data['shift'] = user.shift
        serializer.save(**data)

    def perform_destroy(self, instance):
        from_debt = instance.from_debt
        from_debt.remaining_debt += instance.price
        if from_debt.remaining_debt > 0:
            from_debt.is_paid = False
        from_debt.save()
        instance.delete()

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and user.is_worker:
            return debt_repay_to_pharmacy.WorkerDebtRepayToPharmacySerializer
        return debt_repay_to_pharmacy.DirectorManagerDebtRepayToPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtRepayToPharmacy.objects.filter(from_debt__from_pharmacy_id=user.pharmacy_id)
        else:
            queryset = DebtRepayToPharmacy.objects.filter(from_debt__from_pharmacy__director_id=user.director_id)
        return queryset.select_related('creator', 'from_debt', 'transfer_type').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})
