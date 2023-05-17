from collections import OrderedDict

from django.db.models import Sum
from rest_framework import filters
from rest_framework import serializers
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.firms.models import FirmReport


class FirmReportSerializer(serializers.ModelSerializer):
    pharmacy = serializers.StringRelatedField()
    firm = serializers.StringRelatedField()
    creator = serializers.StringRelatedField()

    class Meta:
        model = FirmReport
        fields = '__all__'


class CustomLimitOffsetPagination(LimitOffsetPagination):

    def get_paginated_response(self, data, dct):
        return Response(OrderedDict([
            ('count', self.count),
            ('income_not_transfer_total_price', dct['income_not_transfer_total_price']),
            ('income_transfer_total_price', dct['income_transfer_total_price']),
            ('expense_not_transfer_total_price', dct['expense_not_transfer_total_price']),
            ('expense_transfer_total_price', dct['expense_transfer_total_price']),
            ('total_debt', dct['total_debt']),
            ('results', data)
        ]))


class FirmReportAPIView(ReadOnlyModelViewSet):
    pagination_class = CustomLimitOffsetPagination
    serializer_class = FirmReportSerializer
    queryset = FirmReport.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'report_date': ['gte', 'lte'],
        'pharmacy_id': ['exact'],
        'firm_id': ['exact']
    }

    def get_paginated_response(self, data, dct):
        return self.paginator.get_paginated_response(data, dct)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).order_by('created_at')
        income_not_transfer_total_price = queryset.filter(
            income__isnull=False, is_transfer=False).aggregate(Sum('price'))
        income_transfer_total_price = queryset.filter(
            income__isnull=False, is_transfer=True).aggregate(Sum('price'))
        expense_not_transfer_total_price = queryset.filter(
            expense__isnull=False, is_transfer=False).aggregate(Sum('price'))
        expense_transfer_total_price = queryset.filter(
            expense__isnull=False, is_transfer=True).aggregate(Sum('price'))
        total_debt = queryset.filter(
            income__isnull=False, income__is_paid=False).aggregate(price__sum=Sum('income__remaining_debt'))
        dct = {
            'income_not_transfer_total_price': income_not_transfer_total_price['price__sum'],
            'income_transfer_total_price': income_transfer_total_price['price__sum'],
            'expense_not_transfer_total_price': expense_not_transfer_total_price['price__sum'],
            'expense_transfer_total_price': expense_transfer_total_price['price__sum'],
            'total_debt': total_debt['price__sum'],
        }
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data, dct)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
