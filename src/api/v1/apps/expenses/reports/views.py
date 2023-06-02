from collections import OrderedDict

from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import ExpenseReportMonth
from ..models import PharmacyExpense


class ExpenseSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    expense_type = serializers.StringRelatedField()
    from_pharmacy = serializers.StringRelatedField()

    class Meta:
        model = PharmacyExpense
        fields = ['creator', 'expense_type', 'from_pharmacy', 'price', 'created_at', 'report_date', 'second_name']


class CustomPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        total_month_price = data['total_month_price']
        del data['total_month_price']
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_month_price', total_month_price),
            ('results', data['results'])
        ]))


class ExpenseAPIView(ReadOnlyModelViewSet):
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    serializer_class = ExpenseSerializer
    filterset_fields = {
        'report_date': ['year', 'month'],
        'from_pharmacy': ['exact'],
        'expense_type': ['exact']
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        month = request.query_params.get('report_date__month')
        year = request.query_params.get('report_date__year')
        from_pharmacy = request.query_params.get('from_pharmacy')
        expense_type = request.query_params.get('expense_type')
        total_month_price = None
        if month and year and from_pharmacy:
            try:
                if expense_type:
                    total_month_price = ExpenseReportMonth.objects.get(
                        month=month, year=year, pharmacy_id=from_pharmacy, expense_type_id=expense_type).price
                else:
                    total_month_price = ExpenseReportMonth.objects.get(
                        month=month, year=year, pharmacy_id=from_pharmacy).price
            except ExpenseReportMonth.DoesNotExist:
                total_month_price = None
        data = {
            'total_month_price': total_month_price,
            'results': serializer.data
        }
        return self.get_paginated_response(data)

    def get_queryset(self):
        user = self.request.user
        queryset = PharmacyExpense.objects.filter(from_pharmacy__director_id=user.director_id).select_related(
            'creator', 'expense_type', 'from_pharmacy').order_by('-created_at')
        return queryset


class ExpenseReportMonthSerializer(serializers.ModelSerializer):
    pharmacy = serializers.StringRelatedField()
    expense_type = serializers.StringRelatedField()

    class Meta:
        model = ExpenseReportMonth
        fields = '__all__'


class ExpenseReportMonthAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    serializer_class = ExpenseReportMonthSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filterset_fields = ['year', 'pharmacy', 'expense_type']

    def get_queryset(self):
        user = self.request.user
        queryset = ExpenseReportMonth.objects.filter(pharmacy__director_id=user.director_id)
        return queryset.select_related('pharmacy', 'expense_type').order_by('month')
