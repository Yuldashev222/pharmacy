from datetime import date

from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from . import serializers
from .models import FirmIncome, FirmFromPharmacyExpense, FirmFromDebtExpense


class FirmAPIViewSet(ModelViewSet):
    serializer_class = serializers.FirmSerializer

    def perform_create(self, serializer):
        serializer.save(director_id=self.request.user.director_id)

    def get_queryset(self):
        return self.request.user.firms_all().order_by('-created_at')

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]


class FirmIncomeAPIViewSet(ModelViewSet):
    serializer_class = serializers.FirmIncomeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_paid', 'report_date']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return FirmIncome.objects.filter(from_firm__director_id=self.request.user.director_id).order_by('-created_at')


class FirmFromPharmacyExpenseAPIViewSet(CreateModelMixin, ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return serializers.WorkerFirmFromPharmacyExpenseSerializer
        return serializers.DirectorManagerFirmFromPharmacyExpenseSerializer

    def perform_create(self, serializer):
        user = self.request.user
        data = {
            'report_date': date.today()
        }
        if user.is_worker:
            data['shift'] = user.shift
            data['from_pharmacy_id'] = user.pharmacy_id
        serializer.save(**data)

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = FirmFromPharmacyExpense.objects.filter(
                report_date=date.today(),
                shift=user.shift,
                from_pharmacy_id=user.pharmacy_id
            )
        else:
            queryset = FirmFromPharmacyExpense.objects.filter(creator__director_id=user.director_id)
        return queryset.filter().order_by('-created_at')


class FirmFromDebtExpenseAPIViewSet(CreateModelMixin, ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]
    serializer_class = serializers.FirmFromDebtExpenseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = FirmFromDebtExpense.objects.filter(
                from_debt__report_date=date.today(),
                from_debt__shift=user.shift,
                from_debt__to_pharmacy_id=user.pharmacy_id
            )
        else:
            queryset = FirmFromDebtExpense.objects.filter(to_firm__director_id=user.director_id)
        return queryset.filter().order_by('-id')


class FirmExpenseVerify(CreateModelMixin, GenericViewSet):
    serializer_class = serializers.FirmExpenseVerifySerializer
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_201_CREATED)
