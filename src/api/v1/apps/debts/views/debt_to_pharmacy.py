from datetime import date
from rest_framework.response import Response
from rest_framework import filters
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.accounts.permissions import NotProjectOwner
from api.v1.apps.companies.permissions import WorkerTodayObject

from ..models import DebtToPharmacy, DebtRepayFromPharmacy
from ..serializers import debt_to_pharmacy, debt_repay_from_pharmacy


class DebtToPharmacyAPIView(ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_paid', 'report_date', 'shift', 'to_pharmacy']
    search_fields = ['from_who', 'desc']

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(
                report_date=date.today(), to_pharmacy_id=user.pharmacy_id, shift=user.shift
            )
        else:
            serializer.save()

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.request.user.is_worker and self.action not in ['list', 'retrieve']:
            permission_classes += [WorkerTodayObject]
        return [permission() for permission in self.permission_classes]

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return debt_to_pharmacy.WorkerDebtToPharmacySerializer
        return debt_to_pharmacy.DirectorManagerDebtToPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtToPharmacy.objects.filter(to_pharmacy_id=user.pharmacy_id, is_paid=False)
        else:
            queryset = DebtToPharmacy.objects.filter(to_pharmacy__director_id=user.director_id)
        queryset = queryset.exclude(
            to_firm_expense__isnull=False, to_firm_expense__is_verified=False
        ).order_by('-created_at')
        return queryset


class TodayDebtToPharmacyAPIView(DebtToPharmacyAPIView):
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})


class DebtRepayFromPharmacyAPIView(ModelViewSet):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'to_debt__to_pharmacy']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.request.user.is_worker and self.action not in ['list', 'retrieve']:
            permission_classes += [WorkerTodayObject]
        return [permission() for permission in self.permission_classes]

    def perform_destroy(self, instance):
        to_debt = instance.to_debt
        to_debt.remaining_debt += instance.price
        if to_debt.remaining_debt > 0:
            to_debt.is_paid = False
        to_debt.save()
        instance.delete()

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(
                shift=user.shift,
                report_date=date.today()
            )
        else:
            serializer.save()

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return debt_repay_from_pharmacy.WorkerDebtRepayFromPharmacySerializer
        return debt_repay_from_pharmacy.DirectorManagerDebtRepayFromPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtRepayFromPharmacy.objects.filter(
                to_debt__to_pharmacy_id=user.pharmacy_id,
                shift=user.shift,
                report_date=date.today()
            )
        else:
            queryset = DebtRepayFromPharmacy.objects.filter(to_debt__to_pharmacy__director_id=user.director_id)
        return queryset.order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})
