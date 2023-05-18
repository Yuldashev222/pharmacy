from datetime import date
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.accounts.permissions import NotProjectOwner
from api.v1.apps.companies.permissions import WorkerTodayObject

from ..models import DebtFromPharmacy, DebtRepayToPharmacy
from ..serializers import debt_from_pharmacy, debt_repay_to_pharmacy


class DebtFromPharmacyAPIView(ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_paid', 'report_date', 'shift', 'is_client']
    search_fields = ['to_who', 'desc']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.request.user.is_worker and self.action not in ['list', 'retrieve']:  # last
            permission_classes += [WorkerTodayObject]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(
                report_date=date.today(),
                from_pharmacy_id=user.pharmacy_id,
                shift=user.shift
            )
        else:
            serializer.save()

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return debt_from_pharmacy.WorkerDebtFromPharmacySerializer
        return debt_from_pharmacy.DirectorManagerDebtFromPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy_id=user.pharmacy_id)
        else:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy__director_id=user.director_id)
        return queryset.order_by('-created_at')


class DebtRepayToPharmacyAPIView(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'from_debt__is_client']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.request.user.is_worker and self.action not in ['list', 'retrieve']:
            permission_classes += [WorkerTodayObject]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(report_date=date.today(), shift=user.shift)
        else:
            serializer.save()

    def perform_destroy(self, instance):
        from_debt = instance.from_debt
        from_debt.remaining_debt += instance.price
        if from_debt.remaining_debt > 0:
            from_debt.is_paid = False
        from_debt.save()
        instance.delete()

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return debt_repay_to_pharmacy.WorkerDebtRepayToPharmacySerializer
        return debt_repay_to_pharmacy.DirectorManagerDebtRepayToPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtRepayToPharmacy.objects.filter(from_debt__from_pharmacy_id=user.pharmacy_id)
        else:
            queryset = DebtRepayToPharmacy.objects.filter(from_debt__from_pharmacy__director_id=user.director_id)
        return queryset.order_by('-created_at')

