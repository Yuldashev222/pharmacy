from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from .models import Client
from .serializers import ClientSerializer


class ClientAPIViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action == 'destroy':
            permission_classes += [(IsDirector | IsManager)]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            queryset = Client.objects.filter(company__in=user.companies.all())
        else:
            queryset = Client.objects.filter(company_id=user.company_id)
        return queryset.order_by('-created_at')
