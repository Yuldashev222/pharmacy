from datetime import date

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner

from ..models import DebtToPharmacy, DebtRepayFromPharmacy
from ..serializers import debt_to_pharmacy, debt_repay_from_pharmacy


class DebtToPharmacyAPIView(ModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return debt_to_pharmacy.WorkerDebtToPharmacySerializer
        return debt_to_pharmacy.DirectorManagerDebtToPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtToPharmacy.objects.filter(
                to_pharmacy_id=user.pharmacy_id,
                report__report_date=date.today(),
                shift=user.shift)
        else:
            queryset = DebtToPharmacy.objects.filter(to_pharmacy__director_id=user.director_id)
        return queryset.order_by('-created_at')


class DebtRepayFromPharmacyAPIView(ModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return debt_repay_from_pharmacy.WorkerDebtRepayFromPharmacySerializer
        return debt_repay_from_pharmacy.DirectorManagerDebtRepayFromPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtRepayFromPharmacy.objects.filter(
                to_debt__to_pharmacy_id=user.pharmacy_id,
                report__report_date=date.today(),
                shift=user.shift
            )
        else:
            queryset = DebtRepayFromPharmacy.objects.filter(to_debt__to_pharmacy__director_id=user.director_id)
        return queryset.order_by('-created_at')
