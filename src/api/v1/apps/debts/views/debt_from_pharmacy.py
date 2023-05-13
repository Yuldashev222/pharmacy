from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.accounts.permissions import NotProjectOwner

from ..models import DebtFromPharmacy, DebtRepayToPharmacy
from ..serializers import debt_from_pharmacy, debt_repay_to_pharmacy


class DebtFromPharmacyAPIView(ModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_paid']

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
    queryset = DebtRepayToPharmacy.objects.all()
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def perform_destroy(self, instance):
        to_debt = instance.to_debt
        to_debt.remaining_debt += instance.price
        if to_debt.remaining_debt > 0:
            to_debt.is_paid = False
        to_debt.save()
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
