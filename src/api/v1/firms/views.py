from datetime import date
from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.pharmacies.services import get_worker_report_date
from api.v1.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from . import serializers
from .models import FirmIncome, FirmExpense, Firm, FirmReturnProduct


class FirmAPIViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name']
    serializer_class = serializers.FirmSerializer

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(director_id=user.director_id, creator_id=user.id)

    def get_queryset(self):
        return Firm.objects.filter(director_id=self.request.user.director_id).select_related('creator',
                                                                                             'director'
                                                                                             ).order_by('-created_at')

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]


class FirmIncomeAPIViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_paid', 'report_date', 'from_firm']

    def get_serializer_class(self):
        if self.action in ('update', 'partial_update'):
            return serializers.FirmIncomeUpdateSerializer
        return serializers.FirmIncomeSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsDirector]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(creator_id=self.request.user.id)

    def get_queryset(self):
        return FirmIncome.objects.filter(from_firm__director_id=self.request.user.director_id
                                         ).select_related('creator',
                                                          'from_firm'
                                                          ).order_by('-created_at')


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
        data = {'creator_id': user.id}
        if user.is_worker:
            data['shift'] = user.shift
            data['from_pharmacy_id'] = user.pharmacy_id
        serializer.save(**data)

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = FirmExpense.objects.filter(report_date=get_worker_report_date(user.pharmacy.last_shift_end_hour),
                                                  shift=user.shift,
                                                  from_pharmacy_id=user.pharmacy_id)
        else:
            queryset = FirmExpense.objects.filter(creator__director_id=user.director_id)

        return queryset.filter(is_verified=True).select_related('creator',
                                                                'transfer_type',
                                                                'from_pharmacy',
                                                                'to_firm',
                                                                'from_user').order_by('-created_at')


class FirmReturnProductAPIViewSet(CreateModelMixin, ReadOnlyModelViewSet):  # last
    serializer_class = serializers.FirmReturnProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date']  # last

    def get_permissions(self):
        permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes = [IsAuthenticated, IsDirector]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(report_date=date.today(), creator_id=self.request.user.id)

    def get_queryset(self):
        user = self.request.user
        queryset = FirmReturnProduct.objects.filter(creator__director_id=user.director_id,
                                                    is_verified=True
                                                    ).select_related('creator', 'firm_income__from_firm')
        return queryset.order_by('-created_at')


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
