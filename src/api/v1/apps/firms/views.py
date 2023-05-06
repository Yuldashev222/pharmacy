from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from .models import FirmIncome
from .serializers import FirmSerializer, FirmIncomeSerializer


class FirmAPIViewSet(ModelViewSet):
    serializer_class = FirmSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            queryset = user.director_firms_all()
        else:
            queryset = user.employee_firms_all()
        return queryset.order_by('-created_at')

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]


class FirmIncomeAPIViewSet(ModelViewSet):
    serializer_class = FirmIncomeSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        if self.action == 'destroy':
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            queryset = FirmIncome.objects.filter(from_firm__company__in=user.companies.all())
        else:
            queryset = FirmIncome.objects.filter(from_firm__company_id=user.company_id)
        return queryset.order_by('-created_at')
