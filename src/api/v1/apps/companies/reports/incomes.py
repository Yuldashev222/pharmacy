from collections import OrderedDict

from django.utils.encoding import escape_uri_path
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from api.v1.apps.accounts.permissions import IsDirector, IsManager

from ..enums import MONTHS
from .models import AllPharmacyIncomeReportMonth


class AllPharmacyIncomeReportMonthSerializer(ModelSerializer):
    class Meta:
        model = AllPharmacyIncomeReportMonth
        fields = ['month', 'price', 'receipt_price']


class AllPharmacyIncomeReportMonthExcelSerializer(ModelSerializer):
    class Meta:
        model = AllPharmacyIncomeReportMonth
        fields = ['year', 'month', 'price']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['month'] = MONTHS[ret['month']]
        return ret


class AllPharmacyIncomeReportMonthAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    filterset_fields = ['year']
    filter_backends = [DjangoFilterBackend]
    serializer_class = AllPharmacyIncomeReportMonthSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]

    def get_queryset(self):
        user = self.request.user
        queryset = AllPharmacyIncomeReportMonth.objects.filter(director_id=user.director_id)
        return queryset.order_by('month')


class AllPharmacyIncomeReportMonthExcelAPIView(XLSXFileMixin, AllPharmacyIncomeReportMonthAPIView):
    serializer_class = AllPharmacyIncomeReportMonthExcelSerializer
    renderer_classes = (XLSXRenderer,)

    def get_filename(self, request=None, *args, **kwargs):
        year = request.query_params.get('year')
        return f'company_income_{year}.xlsx'

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
            "Yil",
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
