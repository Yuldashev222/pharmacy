from datetime import date

from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin

from api.v1.apps.reports.models import Report
from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import PharmacyExpense, PharmacyExpenseHistory
from .serializers import (
    WorkerPharmacyExpenseSerializer,
    PharmacyExpenseHistorySerializer,
    DirectorManagerPharmacyExpenseSerializer
)


class PharmacyExpenseAPIViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.request.user.is_worker():
            return WorkerPharmacyExpenseSerializer
        return DirectorManagerPharmacyExpenseSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker():
            serializer.save(from_pharmacy_id=user.pharmacy_id, shift=user.shift,
                            report_id=Report.objects.get_or_create(report_date=date.today())[0].id)
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.is_director():
            queryset = PharmacyExpense.objects.filter(from_pharmacy__in=user.director_pharmacies_all())
        elif user.is_manager():
            queryset = PharmacyExpense.objects.filter(from_pharmacy__in=user.manager_pharmacies_all())
        else:
            queryset = PharmacyExpense.objects.filter(from_pharmacy_id=user.pharmacy_id,
                                                      report__report_date=date.today())
        return queryset


class PharmacyExpenseHistoryAPIView(ListModelMixin,
                                    RetrieveModelMixin,
                                    DestroyModelMixin,
                                    GenericViewSet):
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    serializer_class = PharmacyExpenseHistorySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_director():
            return PharmacyExpenseHistory.objects.filter(
                pharmacy_expense__from_pharmacy__in=user.director_pharmacies_all())
        return PharmacyExpenseHistory.objects.filter(pharmacy_expense__from_pharmacy__in=user.manager_pharmacies_all())
