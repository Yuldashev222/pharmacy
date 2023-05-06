from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector

from .serializers import PharmacySerializer


class PharmacyAPIViewSet(ModelViewSet):
    serializer_class = PharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_director:
            queryset = user.director_pharmacies_all()
        else:
            queryset = user.employee_pharmacies_all()
        return queryset

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]
