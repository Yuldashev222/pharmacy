from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from api.v1.accounts.permissions import NotProjectOwner, IsProjectOwner
from api.v1.offers.models import Offer

from .serializers import OfferCreateSerializer, OfferUpdateSerializer, OfferRetrieveSerializer


class OfferAPIView(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'status': ['exact'],
        'created_at': ['month', 'year', 'day'],
    }

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_project_owner and obj.status == 'n':
            obj.status = 'p'
            obj.save()
        return obj

    def perform_create(self, serializer):
        serializer.save(creator_id=self.request.user.id)

    def get_serializer_class(self):
        serializer_class = OfferRetrieveSerializer
        if self.action == 'create':
            serializer_class = OfferCreateSerializer
        elif self.action in ['update', 'partial_update']:
            serializer_class = OfferUpdateSerializer
        return serializer_class

    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.action == 'create':
            permission_classes += [NotProjectOwner]
        elif self.action in ['update', 'partial_update']:
            permission_classes += [IsProjectOwner]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_project_owner:
            queryset = Offer.objects.all()
        else:
            queryset = Offer.objects.filter(creator_id=user.id)
        return queryset.select_related('creator').order_by('-created_at')
