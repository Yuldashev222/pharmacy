from datetime import date
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from . import serializers
from .models import FirmIncome, FirmExpense, Firm, FirmReturnProduct


class FirmAPIViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'phone_number1', 'phone_number2', 'phone_number3', 'address', 'desc']
    serializer_class = serializers.FirmSerializer

    def perform_create(self, serializer):
        serializer.save(director_id=self.request.user.director_id)

    def get_queryset(self):
        return Firm.objects.filter(director_id=self.request.user.director_id).order_by('-created_at')

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]


class FirmIncomeAPIViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_paid', 'report_date', 'shift', 'from_firm']

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return serializers.FirmIncomeUpdateSerializer
        return serializers.FirmIncomeSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsDirector]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return FirmIncome.objects.filter(from_firm__director_id=self.request.user.director_id).order_by('-created_at')


class FirmExpenseAPIViewSet(CreateModelMixin, ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'from_pharmacy']

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return serializers.WorkerFirmExpenseSerializer
        return serializers.DirectorManagerFirmExpenseSerializer

    def perform_create(self, serializer):
        user = self.request.user
        data = {
            'report_date': date.today()
        }
        if user.is_worker:
            data['shift'], data['from_pharmacy_id'] = user.shift, user.pharmacy_id
        serializer.save(**data)

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = FirmExpense.objects.filter(
                report_date=date.today(), shift=user.shift, from_pharmacy_id=user.pharmacy_id
            )
        else:
            queryset = FirmExpense.objects.filter(creator__director_id=user.director_id)
        return queryset.filter(is_verified=True).order_by('-created_at')


class FirmReturnProductAPIViewSet(CreateModelMixin, ReadOnlyModelViewSet):
    serializer_class = serializers.FirmReturnProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'firm_income']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner, (IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes = [IsAuthenticated, NotProjectOwner, IsDirector]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(report_date=date.today())

    def get_queryset(self):
        user = self.request.user
        queryset = FirmReturnProduct.objects.filter(creator__director_id=user.director_id)
        return queryset.filter(is_verified=True).order_by('-created_at')


class FirmExpenseVerify(CreateModelMixin, GenericViewSet):
    serializer_class = serializers.FirmExpenseVerifySerializer
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_201_CREATED)


class FirmReturnProductVerify(CreateModelMixin, GenericViewSet):
    serializer_class = serializers.FirmReturnProductVerifySerializer
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(status=status.HTTP_201_CREATED)
