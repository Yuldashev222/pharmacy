from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector

from .serializers import PharmacySerializer


class PharmacyAPIViewSet(ModelViewSet):
    serializer_class = PharmacySerializer

    def perform_create(self, serializer):
        serializer.save(director_id=self.request.user.director_id)

    def get_queryset(self):
        user = self.request.user
        return user.pharmacies_all()

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]
