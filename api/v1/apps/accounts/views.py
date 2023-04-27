from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from . import serializers as user_serializers

from .models import CustomUser, Worker


class UserReadOnlyModelAPIViewSet(ReadOnlyModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = user_serializers.UserReadOnlySerializer
