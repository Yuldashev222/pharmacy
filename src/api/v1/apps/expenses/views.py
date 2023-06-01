from datetime import date
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from .models import UserExpense, PharmacyExpense, ExpenseType
from .serializers import user_expense, pharmacy_expense


class ExpenseTypeAPIViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    serializer_class = pharmacy_expense.ExpenseTypeSerializer

    def get_queryset(self):
        return ExpenseType.objects.filter(director_id=self.request.user.director_id).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(director_id=self.request.user.director_id)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        return [permission() for permission in permission_classes]


class UserExpenseAPIViewSet(ModelViewSet):
    pagination_class = None

    permission_classes = [IsAuthenticated, NotProjectOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'expense_type': ['exact', 'gte'],
        'report_date': ['exact'],
        'shift': ['exact'],
        'to_pharmacy': ['exact']
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(shift=user.shift, report_date=date.today(), to_pharmacy_id=user.pharmacy_id)
        else:
            serializer.save()

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return user_expense.WorkerUserExpenseSerializer
        return user_expense.DirectorManagerUserExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = UserExpense.objects.filter(from_user__director_id=user.director_id)
        if user.is_worker:
            queryset = queryset.filter(report_date=date.today(), shift=user.shift)
        return queryset.order_by('-created_at')


class PharmacyExpenseAPIViewSet(ModelViewSet):
    pagination_class = None

    permission_classes = [IsAuthenticated, NotProjectOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'expense_type': ['exact', 'gte'],
        'shift': ['exact'],
        'report_date': ['exact'],
        'from_pharmacy': ['exact']
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(
                shift=user.shift, report_date=date.today(), from_pharmacy_id=user.pharmacy_id
            )
        else:
            serializer.save()

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
                report_date=date.today(),
                shift=user.shift
            )
        else:
            queryset = PharmacyExpense.objects.filter(
                from_pharmacy__director_id=user.director_id
            )
        return queryset.order_by('-created_at')
