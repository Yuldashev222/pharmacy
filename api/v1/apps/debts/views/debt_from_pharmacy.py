from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.enums import UserRole
from api.v1.apps.accounts.permissions import NotProjectOwner

from ..models import DebtFromPharmacy, DebtRepayToPharmacy
from ..serializers import debt_from_pharmacy, debt_repay_to_pharmacy


class DebtFromPharmacyAPIView(ModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_serializer_class(self):
        if self.request.user.role == UserRole.w.name:
            return debt_from_pharmacy.WorkerDebtFromPharmacySerializer
        return debt_from_pharmacy.DirectorManagerDebtFromPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.w.name:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy_id=user.pharmacy_id)
        elif user.role == UserRole.m.name:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy__company_id=user.company_id)
        else:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy__company__in=user.companies_all())
        return queryset


class DebtRepayToPharmacyAPIView(ModelViewSet):
    queryset = DebtRepayToPharmacy.objects.all()
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_serializer_class(self):
        if self.request.user.role == UserRole.w.name:
            return debt_repay_to_pharmacy.WorkerDebtRepayToPharmacySerializer
        return debt_repay_to_pharmacy.DirectorManagerDebtRepayToPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.w.name:
            queryset = DebtRepayToPharmacy.objects.filter(from_debt__from_pharmacy_id=user.pharmacy_id)
        elif user.role == UserRole.m.name:
            queryset = DebtRepayToPharmacy.objects.filter(from_debt__from_pharmacy__company_id=user.company_id)
        else:
            queryset = DebtRepayToPharmacy.objects.filter(from_debt__from_pharmacy__company__in=user.companies_all())
        return queryset
