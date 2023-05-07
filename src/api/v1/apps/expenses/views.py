from datetime import date
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.reports.models import Report
from api.v1.apps.companies.models import Company
from api.v1.apps.accounts.permissions import NotProjectOwner

from .models import UserExpense, PharmacyExpense
from .serializers import user_expense, pharmacy_expense


class UserExpenseAPIViewSet(ModelViewSet):
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

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return user_expense.WorkerUserExpenseSerializer
        if user.is_director:
            return user_expense.DirectorUserExpenseSerializer
        return user_expense.ManagerUserExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            queryset = UserExpense.objects.filter(
                Q(from_user__company__in=user.companies.all()) | Q(from_user_id=user.id)
            )
        else:
            director_id = Company.objects.get(pk=user.company_id).director_id
        if user.is_worker:
            queryset = UserExpense.objects.filter(
                (Q(from_user__company_id=user.company_id) | Q(from_user_id=director_id))
                & Q(report__report_date=date.today()) & Q(shift=user.shift)
            )
        elif user.is_manager:
            queryset = UserExpense.objects.filter(
                (Q(from_user__company_id=user.company_id) | Q(from_user_id=director_id))  # all director view
            )
        return queryset


class PharmacyExpenseAPIViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(
                shift=user.shift,
                report_id=Report.objects.get_or_create(report_date=date.today())[0].id,
                from_pharmacy_id=user.pharmacy_id
            )
        else:
            serializer.save()

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return pharmacy_expense.WorkerPharmacyExpenseSerializer
        if user.is_director:
            return pharmacy_expense.DirectorPharmacyExpenseSerializer
        return pharmacy_expense.ManagerPharmacyExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            queryset = PharmacyExpense.objects.filter(
                from_pharmacy__in=user.director_pharmacies_all()
            )
        elif user.is_manager:
            queryset = PharmacyExpense.objects.filter(
                from_pharmacy__in=user.employee_pharmacies_all()
            )
        else:
            queryset = PharmacyExpense.objects.filter(
                from_pharmacy_id=user.pharmacy_id,
                report__report_date=date.today(),
                shift=user.shift
            )
        return queryset
