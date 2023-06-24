from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.pharmacies.services import get_worker_report_date
from api.v1.accounts.permissions import NotProjectOwner, IsDirector, IsManager

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
        data = {'creator_id': user.id}
        if user.is_worker:
            data['shift'] = user.shift
            data['report_date'] = get_worker_report_date(user.pharmacy.last_shift_end_hour)
            data['to_pharmacy_id'] = user.pharmacy_id
        serializer.save(**data)

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return user_expense.WorkerUserExpenseSerializer
        return user_expense.DirectorManagerUserExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = UserExpense.objects.filter(from_user__director_id=user.director_id)
        if user.is_worker:
            queryset = queryset.filter(report_date=get_worker_report_date(user.pharmacy.last_shift_end_hour),
                                       shift=user.shift,
                                       to_pharmacy_id=user.pharmacy_id)

        return queryset.filter(to_user__isnull=False).select_related('creator',
                                                                     'expense_type',
                                                                     'transfer_type',
                                                                     'to_user',
                                                                     'from_user',
                                                                     'to_pharmacy').order_by('-id')


class PharmacyExpenseAPIViewSet(ModelViewSet):
    pagination_class = None

    permission_classes = [IsAuthenticated, NotProjectOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'expense_type': ['exact', 'gte', 'gt'],
        'shift': ['exact'],
        'report_date': ['exact'],
        'from_pharmacy': ['exact']
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})

    def perform_create(self, serializer):
        user = self.request.user
        data = {'creator_id': user.id}
        if user.is_worker:
            data['shift'] = user.shift
            data['report_date'] = get_worker_report_date(user.pharmacy.last_shift_end_hour)
            data['from_pharmacy_id'] = user.pharmacy_id
        serializer.save(**data)

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return pharmacy_expense.WorkerPharmacyExpenseSerializer
        return pharmacy_expense.DirectorManagerPharmacyExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = PharmacyExpense.objects.filter(from_pharmacy_id=user.pharmacy_id,
                                                      shift=user.shift,
                                                      report_date=get_worker_report_date(
                                                          user.pharmacy.last_shift_end_hour))
        else:
            queryset = PharmacyExpense.objects.filter(from_pharmacy__director_id=user.director_id)

        return queryset.select_related('creator',
                                       'transfer_type',
                                       'expense_type',
                                       'from_pharmacy',
                                       'to_user').order_by('-id')
