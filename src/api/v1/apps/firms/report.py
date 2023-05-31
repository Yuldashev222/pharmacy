from collections import OrderedDict
from rest_framework import serializers
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.firms.models import FirmReport, FirmDebtByDate


class FirmReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FirmReport
        exclude = ['expense', 'income', 'return_product']


class CustomPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('transfer_debt_in_start_date', data['totals']['transfer_debt_in_start_date']),
            ('not_transfer_debt_in_start_date', data['totals']['not_transfer_debt_in_start_date']),
            ('income_not_transfer_total_price', data['totals']['income_not_transfer_total_price']),
            ('income_transfer_total_price', data['totals']['income_transfer_total_price']),
            ('expense_not_transfer_total_price', data['totals']['expense_not_transfer_total_price']),
            ('expense_transfer_total_price', data['totals']['expense_transfer_total_price']),
            ('results', data['data'])
        ]))


class FirmReportAPIView(ReadOnlyModelViewSet):
    pagination_class = CustomPageNumberPagination
    serializer_class = FirmReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'report_date': ['gte', 'lte'],
        'pharmacy': ['exact'],
        'firm': ['exact']
    }

    def get_queryset(self):
        user = self.request.user
        return FirmReport.objects.filter(creator__director_id=user.director_id).order_by('report_date')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        start_date = request.query_params.get('report_date__gte')
        firm_id = request.query_params.get('firm')
        transfer_debt_in_start_date = 0
        not_transfer_debt_in_start_date = 0
        if start_date and firm_id:
            try:
                obj = FirmDebtByDate.objects.get(report_date=start_date, firm_id=firm_id)
                transfer_debt_in_start_date = obj.transfer_debt
                not_transfer_debt_in_start_date = obj.not_transfer_debt
            except FirmDebtByDate.DoesNotExist:
                pass

        income_not_transfer_total_price = queryset.filter(is_expense=False, is_transfer=False
                                                          ).aggregate(s=Sum('price'))['s']
        income_transfer_total_price = queryset.filter(is_expense=False, is_transfer=True
                                                      ).aggregate(s=Sum('price'))['s']
        expense_not_transfer_total_price = queryset.filter(is_expense=True, is_transfer=False
                                                           ).aggregate(s=Sum('price'))['s']
        expense_transfer_total_price = queryset.filter(is_expense=True, is_transfer=True
                                                       ).aggregate(s=Sum('price'))['s']
        totals = {
            'transfer_debt_in_start_date': transfer_debt_in_start_date,
            'not_transfer_debt_in_start_date': not_transfer_debt_in_start_date,
            'income_not_transfer_total_price': income_not_transfer_total_price if income_not_transfer_total_price else 0,
            'income_transfer_total_price': income_transfer_total_price if income_transfer_total_price else 0,
            'expense_not_transfer_total_price': expense_not_transfer_total_price if expense_not_transfer_total_price else 0,
            'expense_transfer_total_price': expense_transfer_total_price if expense_transfer_total_price else 0
        }
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        data = {
            'totals': totals,
            'data': serializer.data
        }
        return self.get_paginated_response(data)
