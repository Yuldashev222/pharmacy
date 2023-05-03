from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ReadOnlyModelViewSet

from . import serializers as user_serializers

from .enums import UserRole
from .models import Director, Manager, CustomUser, Worker
from .permissions import IsProjectOwner, IsDirector, IsManager
from ..companies.models import Company


class DirectorCreateAPIView(CreateAPIView):
    serializer_class = user_serializers.UserCreateSerializer
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def perform_create(self, serializer):
        serializer.save(role=UserRole.d.name)


class ManagerCreateAPIView(CreateAPIView):
    serializer_class = user_serializers.ManagerCreateSerializer
    permission_classes = [IsAuthenticated, IsDirector]

    def perform_create(self, serializer):
        serializer.save(role=UserRole.m.name)


class WorkerCreateAPIView(CreateAPIView):
    serializer_class = user_serializers.WorkerCreateSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]

    def perform_create(self, serializer):
        serializer.save(role=UserRole.w.name)


class UserReadOnlyAPIView(ReadOnlyModelViewSet):
    serializer_class = user_serializers.UserReadOnlySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.p.name:
            queryset = CustomUser.objects.filter(role=UserRole.d.name)
        elif user.role == UserRole.d.name:
            queryset = CustomUser.objects.filter(company__in=user.companies.all())
        else:
            queryset = CustomUser.objects.filter(company_id=user.company_id)
        return queryset.order_by('-date_joined')


class OwnerRetrieveUpdateAPIView(RetrieveAPIView, UpdateAPIView):
    serializer_class = user_serializers.OwnerRetrieveUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class DirectorUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = user_serializers.DirectorUpdateDestroySerializer
    permission_classes = [IsAuthenticated, IsProjectOwner]

    def get_queryset(self):
        queryset = Director.objects.all()
        return queryset


class ManagerUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = user_serializers.ManagerUpdateDestroySerializer
    permission_classes = [IsAuthenticated, IsDirector]

    def get_queryset(self):
        queryset = Manager.objects.filter(company__in=self.request.user.companies.all())
        return queryset


class WorkerUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = user_serializers.WorkerUpdateDestroySerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]

    def get_queryset(self):
        user = self.request.user
        if user.role == UserRole.d.name:
            queryset = Worker.objects.filter(company__in=user.companies.all())
        else:
            queryset = Worker.objects.filter(company_id=user.company_id)
        return queryset

# company_id 18
# director +998974068633   18
# manager +998974068000   22
# worker +998974068681   22
# print(CustomUser.objects.last().id)
