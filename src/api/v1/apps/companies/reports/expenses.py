from collections import OrderedDict
from rest_framework import serializers
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from django.utils.encoding import escape_uri_path
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.expenses.models import ExpenseType
from api.v1.apps.accounts.permissions import IsDirector, IsManager

from .models import AllExpenseReportMonth
from ..enums import MONTHS


class AllExpenseReportMonthSerializer(serializers.ModelSerializer):
    expense_type = serializers.StringRelatedField()

    class Meta:
        model = AllExpenseReportMonth
        fields = ['month', 'expense_type', 'price']


class AllExpenseReportMonthExcelSerializer(serializers.ModelSerializer):
    expense_type = serializers.StringRelatedField()

    class Meta:
        model = AllExpenseReportMonth
        fields = ['expense_type', 'month', 'price']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['month'] = MONTHS[ret['month']]
        return ret


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


class AllExpenseReportMonthExcelAPIView(XLSXFileMixin, AllExpenseReportMonthAPIView):
    serializer_class = AllExpenseReportMonthExcelSerializer
    renderer_classes = (XLSXRenderer,)

    def get_filename(self, request=None, *args, **kwargs):
        expense_id = request.query_params.get('expense_type')
        try:
            obj = ExpenseType.objects.get(id=expense_id)
        except ExpenseType.DoesNotExist:
            return 'company.xlsx'
        return f'company_expense_by_{obj.name}.xlsx'

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        filename = escape_uri_path(self.get_filename(request=request, *args, **kwargs))
        response["content-disposition"] = f"attachment; filename={filename}"
        total_price = sum(list(map(lambda x: x['price'], response.data)))
        response.data.append(OrderedDict())
        response.data.append(OrderedDict(month='Jami', price=total_price))
        return response

    column_header = {
        'titles': [
            "Xarajat turi",
            "Oy",
            "Miqdor",
        ],
        'column_width': [30, 30, 30],
        'height': 50,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': True,
                'color': 'FF000000',
            },
        },
    }

    body = {
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'FFCCFFCC',
            },
            'alignment': {
                'horizontal': 'center',
                'vertical': 'center',
                'wrapText': True,
                'shrink_to_fit': True,
            },
            'border_side': {
                'border_style': 'thin',
                'color': 'FF000000',
            },
            'font': {
                'name': 'Arial',
                'size': 14,
                'bold': False,
                'color': 'FF000000',
            }
        },
        'height': 40,
    }
