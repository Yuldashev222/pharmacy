from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from . import serializers
from .models import FirmIncome


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

#
# class FirmExpenseAPIViewSet(ModelViewSet):
#
#     def get_serializer_class(self):
#         user = self.request.user
#         if user.is_worker:
#             return serializers.WorkerFirmExpenseSerializer
#         return serializers.DirectorManagerFirmExpenseSerializer
#
#     def get_permissions(self):
#         permission_classes = [IsAuthenticated, NotProjectOwner]
#         if self.action not in ['list', 'retrieve']:
#             permission_classes += [(IsDirector | IsManager)]
#         if self.action == 'destroy':
#             permission_classes += [IsDirector]
#         return [permission() for permission in permission_classes]
#
#     def get_queryset(self):
#         user = self.request.user
#         if user.is_director:
#             queryset = FirmExpense.objects.filter(to_firm__company_id=user.company_id)
#         else:
#             queryset = FirmExpense.objects.filter(to_firm__company_id=user.company_id)
#         return queryset.order_by('-created_at')
