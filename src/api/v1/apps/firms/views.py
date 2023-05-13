from datetime import date
from random import randint

from rest_framework import status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from . import serializers
from .models import FirmIncome, FirmExpense
from ..reports.models import Report


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

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        queryset = FirmIncome.objects.filter(from_firm__director_id=user.director_id)
        return queryset.order_by('-created_at')


class FirmExpenseAPIViewSet(CreateModelMixin, ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return serializers.WorkerFirmExpenseSerializer
        return serializers.DirectorManagerFirmExpenseSerializer

    def perform_create(self, serializer):
        user = self.request.user
        data = {
            'report_id': Report.objects.get_or_create(report_date=date.today())[0].id
        }
        if user.is_worker:
            data['shift'] = user.shift
            data['from_pharmacy_id'] = user.pharmacy_id
        serializer.save(**data)

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = FirmExpense.objects.filter(
                report__report_date=date.today(),
                shift=user.shift,
                from_pharmacy_id=user.pharmacy_id
            )
        else:
            queryset = FirmExpense.objects.filter(creator__director_id=user.director_id)
        return queryset.filter(is_verified=True).order_by('-created_at')


class FirmExpenseVerify(CreateModelMixin, GenericViewSet):
    serializer_class = serializers.FirmExpenseVerifySerializer
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.save(), status=status.HTTP_201_CREATED)