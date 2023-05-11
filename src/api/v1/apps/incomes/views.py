from datetime import date
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager
from api.v1.apps.reports.models import Report

from .models import PharmacyIncome
from .serializers import (
    DirectorManagerPharmacyIncomeSerializer,
    WorkerPharmacyIncomeSerializer,
#    PharmacyIncomeHistorySerializer
)


class PharmacyIncomeAPIViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(
                   shift=user.shift,
                   report_id=Report.objects.get_or_create(report_date=date.today())[0].id,
                   to_pharmacy_id=user.pharmacy_id
            )
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
                to_pharmacy_id=user.pharmacy_id,
                report__report_date=date.today(),
                shift=user.shift
            )
        else:
            queryset = PharmacyIncome.objects.filter(to_pharmacy__director_id=user.director_id)
        return queryset.order_by('-created_at')


#class PharmacyIncomeHistoryAPIView(ListModelMixin,
#                                   RetrieveModelMixin,
#                                   DestroyModelMixin,
#                                   GenericViewSet):
#    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
#    serializer_class = PharmacyIncomeHistorySerializer
#
#    def get_queryset(self):
#        user = self.request.user
#        return PharmacyIncomeHistory.objects.filter(
#            pharmacy_income__to_pharmacy__director_id=user.director_id
#        ).order_by('-id')
