from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.enums import UserRole
from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector

from .models import Pharmacy
from .serializers import PharmacySerializer


class PharmacyAPIViewSet(ModelViewSet):
    serializer_class = PharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_director():
            queryset = Pharmacy.objects.filter(company__in=user.companies.all())
        else:
            queryset = Pharmacy.objects.filter(company_id=user.company_id)
        return queryset

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]
