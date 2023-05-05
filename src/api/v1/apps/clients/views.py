from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.enums import UserRole
from api.v1.apps.accounts.permissions import NotProjectOwner

from .models import Client

from .serializers import ClientSerializer


class ClientAPIViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated, NotProjectOwner]

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.d.name:
            queryset = Client.objects.filter(company__in=user.companies.all())
        else:
            queryset = Client.objects.filter(company_id=user.company_id)
        return queryset.order_by('-created_at')
