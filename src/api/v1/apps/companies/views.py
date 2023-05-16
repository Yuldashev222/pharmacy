from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import api_view, permission_classes

from api.v1.apps.firms.models import Firm
from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.expenses.models import ExpenseType
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.accounts.permissions import IsDirector, NotProjectOwner, IsManager

from .models import Company, TransferMoneyType
from .serializers import CompanySerializer, TransferMoneyTypeSerializer


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


@api_view(['GET'])
@permission_classes([IsAuthenticated, NotProjectOwner])
def company_details(request, *args, **kwargs):
    user = request.user
    data = {
        'transfer_types': TransferMoneyType.objects.filter(
            director_id=user.director_id).values('id', 'name').order_by('-id'),
        'account_expense_types': ExpenseType.objects.filter(
            director_id=user.director_id, is_user_expense=True).values('id', 'name').order_by('-id'),
        'pharmacy_expense_types': ExpenseType.objects.filter(
            director_id=user.director_id, is_user_expense=False).values('id', 'name').order_by('-id'),
        'employees': CustomUser.objects.filter(
            director_id=user.director_id).values('id', 'first_name', 'last_name', 'role').order_by('-id'),
        'firms': Firm.objects.filter(director_id=user.director_id).values('id', 'name').order_by('-id')
    }
    if user.is_worker:
        data['pharmacies'] = Pharmacy.objects.filter(id=user.pharmacy_id).values('id', 'name').order_by('-id')
    else:
        data['pharmacies'] = Pharmacy.objects.filter(director_id=user.director_id).values('id', 'name').order_by('-id')
    return Response(data)


class TransferMoneyTypeAPIViewSet(ModelViewSet):
    serializer_class = TransferMoneyTypeSerializer

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.action not in ['list', 'retrieve']:
            permission_classes += [(IsDirector | IsManager)]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(director_id=user.director_id)

    def get_queryset(self):
        queryset = TransferMoneyType.objects.filter(director_id=self.request.user.director_id)
        return queryset.order_by('-id')
