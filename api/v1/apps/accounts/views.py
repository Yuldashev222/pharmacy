from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from . import serializers as user_serializers

from .enums import UserRole
from .models import Director, Manager
from .permissions import IsProjectOwner, IsOwner, IsDirector


class DirectorAPIViewSet(ModelViewSet):
    serializer_class = user_serializers.DirectorSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.p.name:
            queryset = Director.objects.all()
        else:
            queryset = Director.objects.filter(company_id=user.company_id)
        return queryset.order_by('-date_joined')

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['create', 'delete', 'list']:
            permission_classes += [IsProjectOwner]
        elif self.action == 'update':
            permission_classes += [IsOwner]
        return [permission() for permission in permission_classes]


class ManagerAPIViewSet(ModelViewSet):
    serializer_class = user_serializers.ManagerSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Manager.objects.filter(company_id=user.company_id)
        return queryset.order_by('-date_joined')

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action in ['create', 'delete', 'list']:
            permission_classes += [IsDirector]
        elif self.action == 'update':
            permission_classes += [IsOwner]
        return [permission() for permission in permission_classes]
