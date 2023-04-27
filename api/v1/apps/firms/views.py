from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import IsDirectorOrOwnerOrReadOnly

from .models import Firm
from .serializers import FirmSerializer


class FirmAPIViewSet(ModelViewSet):
    serializer_class = FirmSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Firm.objects.filter(Q(director_id=user.id) | Q(customuser=user)).select_related('director')
