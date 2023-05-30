from datetime import date
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from api.v1.apps.accounts.permissions import NotProjectOwner

from .models import PharmacyIncome
from .serializers import (
    DirectorManagerPharmacyIncomeSerializer,
    WorkerPharmacyIncomeSerializer
)


class PharmacyIncomeAPIViewSet(ModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticated, NotProjectOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'to_pharmacy']

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(
                shift=user.shift, report_date=date.today(), to_pharmacy_id=user.pharmacy_id)
        else:
            serializer.save()

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return WorkerPharmacyIncomeSerializer
        return DirectorManagerPharmacyIncomeSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = PharmacyIncome.objects.filter(
                to_pharmacy_id=user.pharmacy_id, report_date=date.today(), shift=user.shift
            )
        else:
            queryset = PharmacyIncome.objects.filter(to_pharmacy__director_id=user.director_id)
        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})
