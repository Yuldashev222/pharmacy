from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.enums import UserRole
from api.v1.apps.general.permissions import IsOwnerCreator
from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager
from api.v1.apps.reports.permissions import IsTodayDateReport

from .models import PharmacyIncome, PharmacyIncomeHistory
from .serializers import (
    DirectorManagerPharmacyIncomeSerializer,
    WorkerPharmacyIncomeSerializer,
    PharmacyIncomeHistorySerializer
)


class PharmacyIncomeAPIViewSet(ModelViewSet):
    def get_permissions(self):
        user = self.request.user
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if user.is_authenticated and user.role == UserRole.w.name:
            permission_classes += [IsTodayDateReport, IsOwnerCreator]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        user = self.request.user
        if user.role == UserRole.w.name:
            return WorkerPharmacyIncomeSerializer
        return DirectorManagerPharmacyIncomeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.d.name:
            queryset = PharmacyIncome.objects.filter(to_pharmacy__in=user.director_pharmacies_all())
        elif user.role == UserRole.m.name:
            queryset = PharmacyIncome.objects.filter(to_pharmacy__company_id=user.company_id)
        else:
            queryset = PharmacyIncome.objects.filter(to_pharmacy_id=user.pharmacy_id)
        return queryset


class PharmacyIncomeHistoryAPIView(ListModelMixin,
                                   RetrieveModelMixin,
                                   DestroyModelMixin,
                                   GenericViewSet):
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    serializer_class = PharmacyIncomeHistorySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_director():
            return PharmacyIncomeHistory.objects.filter(pharmacy_income__to_pharmacy__in=user.director_pharmacies_all())
        return PharmacyIncomeHistory.objects.filter(pharmacy_income__to_pharmacy__in=user.manager_pharmacies_all())
