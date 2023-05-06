from datetime import date
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from .models import PharmacyIncome, PharmacyIncomeHistory
from .serializers import (
    DirectorManagerPharmacyIncomeSerializer,
    WorkerPharmacyIncomeSerializer,
    PharmacyIncomeHistorySerializer
)


class PharmacyIncomeAPIViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]  # + IsOwnerCreator

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return WorkerPharmacyIncomeSerializer
        return DirectorManagerPharmacyIncomeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            queryset = PharmacyIncome.objects.filter(to_pharmacy__in=user.director_pharmacies_all())
        elif user.is_manager:
            queryset = PharmacyIncome.objects.filter(to_pharmacy__company_id=user.company_id)
        else:
            queryset = PharmacyIncome.objects.filter(to_pharmacy_id=user.pharmacy_id, report__report_date=date.today())
        return queryset


class PharmacyIncomeHistoryAPIView(ListModelMixin,
                                   RetrieveModelMixin,
                                   DestroyModelMixin,
                                   GenericViewSet):
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    serializer_class = PharmacyIncomeHistorySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            return PharmacyIncomeHistory.objects.filter(pharmacy_income__to_pharmacy__in=user.director_pharmacies_all())
        return PharmacyIncomeHistory.objects.filter(pharmacy_income__to_pharmacy__in=user.employee_pharmacies_all())
