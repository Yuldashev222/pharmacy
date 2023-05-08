from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import IsDirector, NotProjectOwner

from .models import Company
from .serializers import CompanySerializer


class CompanyAPIViewSet(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    serializer_class = CompanySerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [IsDirector]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        return Company.objects.filter(director_id=user.director_id)
