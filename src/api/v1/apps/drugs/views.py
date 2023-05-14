from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from .models import Drug
from .serializers import WorkerDrugSerializer, DirectorManagerDrugSerializer


class DrugAPIViewSet(ModelViewSet):
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
            queryset = Drug.objects.filter(pharmacy_id=user.pharmacy_id)
        else:
            queryset = Drug.objects.filter(pharmacy__director_id=user.director_id)
        return queryset.order_by('-created_at')

    def get_serializer_class(self):
        user = self.request.user
        if user.is_worker:
            return WorkerDrugSerializer
        return DirectorManagerDrugSerializer
