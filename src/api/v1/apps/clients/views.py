from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from .models import Client
from .serializers import ClientSerializer


class ClientAPIViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_worker:
            serializer.save(pharmacy_id=user.pharmacy_id)
        else:
            serializer.save()

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action == 'destroy':
            permission_classes += [(IsDirector | IsManager)]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = Client.objects.filter(pharmacy_id=user.pharmacy_id)
        else:
            queryset = Client.objects.filter(pharmacy__director_id=user.director_id)
        return queryset.order_by('-created_at')
