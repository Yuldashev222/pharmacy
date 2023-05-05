from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import IsDirector

from .models import Company
from .serializers import CompanySerializer


class CompanyAPIViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated, IsDirector]
    serializer_class = CompanySerializer

    def get_queryset(self):
        user = self.request.user
        return Company.objects.filter(director_id=user.id).order_by('-created_at')
