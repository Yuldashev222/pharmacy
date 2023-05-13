from datetime import date
from random import randint
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from .models import UserExpense, PharmacyExpense, ExpenseType
from .serializers import user_expense, pharmacy_expense


class ExpenseTypeAPIViewSet(ModelViewSet):
    serializer_class = pharmacy_expense.ExpenseTypeSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(director_id=user.director_id)

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        queryset = ExpenseType.objects.filter(director_id=user.director_id)
        return queryset.order_by('-id')


class UserExpenseAPIViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return user_expense.WorkerUserExpenseSerializer
        return user_expense.DirectorManagerUserExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = UserExpense.objects.filter(from_user__director_id=user.director_id)
        if user.is_worker:
            queryset = queryset.filter(
                report__report_date=date.today(),
                shift=user.shift
            )
        return queryset.order_by('-created_at')


class PharmacyExpenseAPIViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def perform_create(self, serializer):
        serializer.save(verified_code=randint(10000, 99999))

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return pharmacy_expense.WorkerPharmacyExpenseSerializer
        return pharmacy_expense.DirectorManagerPharmacyExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = PharmacyExpense.objects.filter(
                from_pharmacy_id=user.pharmacy_id,
                report__report_date=date.today(),
                shift=user.shift
            )
        else:
            queryset = PharmacyExpense.objects.filter(
                from_pharmacy__director_id=user.director_id
            )
        return queryset.order_by('-created_at')
