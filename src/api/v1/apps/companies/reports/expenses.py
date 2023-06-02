from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import AllExpenseReportMonth


class AllExpenseReportMonthSerializer(serializers.ModelSerializer):
    expense_type = serializers.StringRelatedField()

    class Meta:
        model = AllExpenseReportMonth
        fields = ['month', 'price', 'expense_type']


class AllExpenseReportMonthAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    serializer_class = AllExpenseReportMonthSerializer
    filterset_fields = ['year', 'expense_type']

    def get_queryset(self):
        user = self.request.user
        queryset = AllExpenseReportMonth.objects.filter(director_id=user.director_id)
        return queryset.select_related('expense_type').order_by('month')
