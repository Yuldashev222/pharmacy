from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import NotProjectOwner, IsDirector, IsManager

from .models import Client
from .serializers import ClientSerializer


class ClientAPIViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['phone_number1', 'phone_number2', 'first_name', 'last_name', 'bio', 'birthdate', 'address']
    serializer_class = ClientSerializer

    def perform_create(self, serializer):
        serializer.save(creator_id=self.request.user.id)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action == 'destroy':
            permission_classes += [(IsDirector | IsManager)]
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        return Client.objects.filter(creator__director_id=self.request.user.director_id).order_by('-created_at')
