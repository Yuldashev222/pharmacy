from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from .models import Client
from .serializers import ClientSerializer


class ClientAPIViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def perform_create(self, serializer):
        serializer.save(director_id=self.request.user.director_id)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action == 'destroy':
            permission_classes += [(IsDirector | IsManager)]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        return Client.objects.filter(director_id=user.director_id).order_by('-created_at')
