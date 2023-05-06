from datetime import date
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from api.v1.apps.reports.models import Report
from api.v1.apps.accounts.permissions import IsDirector, IsManager, NotProjectOwner

from .models import Expense, ExpenseHistory
from .serializers import (
    ExpenseSerializer,
    ExpenseHistorySerializer,
    WorkerFromPharmacyExpenseCreateUpdateSerializer,
    DirectorManagerFromPharmacyExpenseCreateUpdateSerializer,
)


class ExpenseAPIViewSet:
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(
                shift=user.shift,
                report_id=Report.objects.get_or_create(report_date=date.today())[0].id
            )
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            queryset = Expense.objects.filter(from_pharmacy__in=user.director_pharmacies_all())
        elif user.is_manager:
            queryset = Expense.objects.filter(from_pharmacy__in=user.employee_pharmacies_all())
        else:
            queryset = Expense.objects.filter(
                from_pharmacy_id=user.pharmacy_id,
                report__report_date=date.today(),
                shift=user.shift
            )
        return queryset


class ExpenseRetrieveDestroyAPIViewSet(ExpenseAPIViewSet,
                                       mixins.DestroyModelMixin,
                                       ReadOnlyModelViewSet):
    serializer_class = ExpenseSerializer


class FromPharmacyExpenseCreateUpdateAPIView(ExpenseAPIViewSet,
                                             mixins.CreateModelMixin,
                                             mixins.UpdateModelMixin,
                                             GenericViewSet):

    def get_serializer_class(self):
        print(self.action)
        if self.request.user.is_worker:
            return WorkerFromPharmacyExpenseCreateUpdateSerializer
        return DirectorManagerFromPharmacyExpenseCreateUpdateSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(
                from_pharmacy_id=user.pharmacy_id,
                shift=user.shift,
                report_id=Report.objects.get_or_create(report_date=date.today())[0].id
            )
        else:
            serializer.save()

    def get_queryset(self):
        return super().get_queryset().filter(from_pharmacy__isnull=False)


# class FromUserExpenseCreateUpdateAPIView(ExpenseAPIViewSet,
#                                          mixins.CreateModelMixin,
#                                          mixins.UpdateModelMixin,
#                                          GenericViewSet):
#
#     def get_serializer_class(self):
#         if self.request.user.is_worker:
#             return WorkerFromUserExpenseCreateSerializer
#         return DirectorManagerFromUserExpenseCreateSerializer
#
#     def get_queryset(self):
#         return super().get_queryset().filter(from_user__isnull=False)


class ExpenseHistoryAPIView(mixins.DestroyModelMixin,
                            ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    serializer_class = ExpenseHistorySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            return ExpenseHistory.objects.filter(
                pharmacy_expense__from_pharmacy__in=user.director_pharmacies_all())
        return ExpenseHistory.objects.filter(pharmacy_expense__from_pharmacy__in=user.employee_pharmacies_all())
