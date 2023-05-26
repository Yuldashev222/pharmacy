from collections import OrderedDict

from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.companies.enums import StaticEnv
from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import ReturnProductReportMonth
from ..models import PharmacyExpense


class ReturnProductSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()

    class Meta:
        model = PharmacyExpense
        fields = ['creator', 'price', 'created_at', 'report_date', 'second_name']


class CustomPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        total_month_price = data['total_month_price']
        del data['total_month_price']
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_month_price', total_month_price),
            ('results', data)
        ]))


class ReturnProductAPIView(ReadOnlyModelViewSet):
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    serializer_class = ReturnProductSerializer
    filterset_fields = {
        'report_date': ['year', 'month'],
        'from_pharmacy': ['exact']
    }

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        month = request.query_params.get('report_date__month')
        year = request.query_params.get('report_date__year')
        total_month_price = None
        if month and year:
            total_month_price = ReturnProductReportMonth.objects.get(month=month, year=year).price

        data = {
            'total_month_price': total_month_price,
            'results': serializer.data
        }
        return self.get_paginated_response(data)

    def get_queryset(self):
        user = self.request.user
        queryset = PharmacyExpense.objects.filter(
            from_pharmacy__director_id=user.director_id,
            expense_type_id=StaticEnv.return_product_id.value
        )
        return queryset.order_by('-created_at')


class ReturnProductReportMonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProductReportMonth
        fields = ['month', 'price']


class ReturnProductReportMonthAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    serializer_class = ReturnProductReportMonthSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filterset_fields = ['year', 'pharmacy']

    def get_queryset(self):
        user = self.request.user
        queryset = ReturnProductReportMonth.objects.filter(director_id=user.director_id)
        return queryset.order_by('month')
