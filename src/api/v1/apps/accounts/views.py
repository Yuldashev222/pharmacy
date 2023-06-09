from rest_framework import filters
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from . import serializers as user_serializers

from .enums import UserRole
from .models import CustomUser
from .permissions import IsProjectOwner, IsDirector, IsManager


class DirectorCreateAPIView(CreateAPIView):
    serializer_class = user_serializers.UserCreateSerializer
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def perform_create(self, serializer):
        serializer.save(role=UserRole.d.name)


class ManagerCreateAPIView(CreateAPIView):
    serializer_class = user_serializers.UserCreateSerializer
    permission_classes = [IsAuthenticated, IsDirector]

    def perform_create(self, serializer):
        serializer.save(role=UserRole.m.name, director_id=self.request.user.director_id)


class WorkerCreateAPIView(CreateAPIView):
    serializer_class = user_serializers.WorkerCreateSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]

    def perform_create(self, serializer):
        serializer.save(role=UserRole.w.name, director_id=self.request.user.director_id)


class UserReadOnlyAPIView(ReadOnlyModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role', 'shift', 'pharmacy']
    search_fields = ['first_name', 'last_name', 'bio', 'address']
    serializer_class = user_serializers.UserReadOnlySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_project_owner:
            queryset = CustomUser.objects.filter(role=UserRole.d.name)
        else:
            queryset = CustomUser.objects.filter(director_id=user.director_id)
        return queryset.select_related('pharmacy', 'director', 'creator').order_by('-date_joined')


class OwnerRetrieveUpdateAPIView(RetrieveAPIView, UpdateAPIView):
    serializer_class = user_serializers.OwnerRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class DirectorUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = user_serializers.DirectorUpdateDestroySerializer
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def get_queryset(self):
        queryset = CustomUser.objects.filter(role=UserRole.d.name).order_by('-date_joined')
        return queryset


class ManagerUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = user_serializers.ManagerUpdateDestroySerializer
    permission_classes = [IsAuthenticated, IsDirector]

    def get_queryset(self):
        return CustomUser.objects.filter(role=UserRole.m.name, director_id=self.request.user.director_id).order_by('-date_joined')


class WorkerUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = user_serializers.WorkerUpdateDestroySerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]

    def get_queryset(self):
        user = self.request.user
        return CustomUser.objects.filter(role=UserRole.w.name, director_id=user.director_id).order_by('-date_joined')

# director_id 1
# company_id 1
# director +998974068622   2
# manager +998974068000   3
# worker +998974068681   4
