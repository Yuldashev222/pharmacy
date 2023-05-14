from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector
from .models import Pharmacy

from .serializers import PharmacySerializer


class PharmacyAPIViewSet(ModelViewSet):
    serializer_class = PharmacySerializer

    def perform_create(self, serializer):
        serializer.save(director_id=self.request.user.director_id)

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = Pharmacy.objects.filter(id=user.pharmacy_id)
        else:
            queryset = Pharmacy.objects.filter(director_id=user.director_id)
        return queryset.order_by('-created_at')

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]
