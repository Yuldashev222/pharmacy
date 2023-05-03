from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.enums import UserRole
from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from .models import Firm, FirmIncome
from .serializers import FirmSerializer, FirmIncomeSerializer


class FirmAPIViewSet(ModelViewSet):
    serializer_class = FirmSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.d.name:
            queryset = Firm.objects.filter(company__in=user.companies.all())
        else:
            queryset = Firm.objects.filter(company_id=user.company_id)
        return queryset

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]


class FirmIncomeAPIViewSet(ModelViewSet):
    serializer_class = FirmIncomeSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]

    def get_queryset(self):
        firm_id = self.request.query_params.get('firm_id', 'no')
        if firm_id == 'no' or not isinstance(firm_id, int):
            raise ValidationError('firm_id not found in query params')
        user = self.request.user
        if user.role == UserRole.d.name:
            queryset = FirmIncome.objects.filter(
                from_firm__company__in=user.companies.all(),
                from_firm_id=firm_id)
        else:
            queryset = Firm.objects.filter(from_firm__company_id=user.company_id, from_firm_id=firm_id)
        return queryset
