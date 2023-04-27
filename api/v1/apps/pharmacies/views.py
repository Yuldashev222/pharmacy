from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import IsDirectorOrOwnerOrReadOnly

from .models import Pharmacy
from .serializers import PharmacySerializer


class PharmacyAPIViewSet(ModelViewSet):
    serializer_class = PharmacySerializer
    permission_classes = [IsAuthenticated, IsDirectorOrOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        return Pharmacy.objects.filter(Q(director_id=user.id) | Q(customuser=user)).select_related('director')
