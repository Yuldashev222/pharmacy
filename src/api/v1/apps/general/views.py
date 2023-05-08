from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import TransferMoneyType, ExpenseType
from .serializers import (
    DirectorTransferMoneyTypeSerializer,
    EmployeeTransferMoneyTypeSerializer,
    DirectorExpenseTypeSerializer,
    EmployeeExpenseTypeSerializer
)


class TransferMoneyTypeAPIViewSet(ModelViewSet):
    def get_serializer_class(self):
        if self.request.user.is_director:
            return DirectorTransferMoneyTypeSerializer
        return EmployeeTransferMoneyTypeSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_manager:
            serializer.save(company_id=user.company_id)
        else:
            serializer.save()

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            queryset = TransferMoneyType.objects.filter(company__in=user.companies.all())
        else:
            queryset = TransferMoneyType.objects.filter(company_id=user.company_id)
        return queryset


class ExpenseTypeAPIViewSet(ModelViewSet):
    def perform_create(self, serializer):
        user = self.request.user
        if user.is_manager:
            serializer.save(company_id=user.company_id)
        else:
            serializer.save()

    def get_serializer_class(self):
        if self.request.user.is_director:
            return DirectorExpenseTypeSerializer
        return EmployeeExpenseTypeSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            queryset = ExpenseType.objects.filter(company__in=user.companies.all())
        else:
            queryset = ExpenseType.objects.filter(company_id=user.company_id)
        return queryset.order_by('-id')
