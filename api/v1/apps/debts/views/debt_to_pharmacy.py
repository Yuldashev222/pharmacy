from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.enums import UserRole
from api.v1.apps.accounts.permissions import NotProjectOwner

from ..models import DebtToPharmacy, DebtRepayFromPharmacy
from ..serializers import debt_to_pharmacy, debt_repay_from_pharmacy


class DebtToPharmacyAPIView(ModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_serializer_class(self):
        if self.request.user.role == UserRole.w.name:
            return debt_to_pharmacy.WorkerDebtToPharmacySerializer
        return debt_to_pharmacy.DirectorManagerDebtToPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.w.name:
            queryset = DebtToPharmacy.objects.filter(to_pharmacy_id=user.pharmacy_id)
        elif user.role == UserRole.m.name:
            queryset = DebtToPharmacy.objects.filter(to_pharmacy__company_id=user.company_id)
        else:
            queryset = DebtToPharmacy.objects.filter(to_pharmacy__company__in=user.companies_all())
        return queryset


class DebtRepayFromPharmacyAPIView(ModelViewSet):
    queryset = DebtRepayFromPharmacy.objects.all()
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_serializer_class(self):
        if self.request.user.role == UserRole.w.name:
            return debt_repay_from_pharmacy.WorkerDebtRepayFromPharmacySerializer
        return debt_repay_from_pharmacy.DirectorManagerDebtRepayFromPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.w.name:
            queryset = DebtRepayFromPharmacy.objects.filter(to_debt__to_pharmacy_id=user.pharmacy_id)
        elif user.role == UserRole.m.name:
            queryset = DebtRepayFromPharmacy.objects.filter(to_debt__to_pharmacy__company_id=user.company_id)
        else:
            queryset = DebtRepayFromPharmacy.objects.filter(to_debt__to_pharmacy__company__in=user.companies_all())
        return queryset
