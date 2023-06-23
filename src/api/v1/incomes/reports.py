from collections import OrderedDict
from rest_framework import serializers
from drf_excel.renderers import XLSXRenderer
from django.utils.encoding import escape_uri_path
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.companies.enums import MONTHS
from api.v1.pharmacies.models import Pharmacy
from api.v1.accounts.permissions import IsDirector, IsManager

from .models import PharmacyIncomeReportMonth


class PharmacyIncomeReportMonthSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyIncomeReportMonth
        fields = ['month', 'price']


class PharmacyIncomeReportMonthAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    serializer_class = PharmacyIncomeReportMonthSerializer
    filterset_fields = ['year', 'pharmacy']

    def get_queryset(self):
        user = self.request.user
        queryset = PharmacyIncomeReportMonth.objects.filter(pharmacy__director_id=user.director_id)
        return queryset.order_by('month')


class PharmacyIncomeReportMonthExcelSerializer(serializers.ModelSerializer):
    class Meta:
        model = PharmacyIncomeReportMonth
        fields = ['month', 'price']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['month'] = MONTHS[ret['month']]
        return ret


class PharmacyIncomeReportMonthExcelAPIView(PharmacyIncomeReportMonthAPIView):
    serializer_class = PharmacyIncomeReportMonthExcelSerializer
    renderer_classes = (XLSXRenderer,)

    def get_filename(self, request=None, *args, **kwargs):
        year = request.query_params.get('year')
        pharmacy_id = request.query_params.get('pharmacy')
        try:
            pharmacy = Pharmacy.objects.get(id=pharmacy_id)
        except Pharmacy.DoesNotExist:
            return f'{year}_report.xlsx'
        return f'{year}_{"".join(str(pharmacy).split())}_report.xlsx'

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        filename = escape_uri_path(self.get_filename(request=request, *args, **kwargs))
        response["content-disposition"] = f"attachment; filename={filename}"

        try:
            total_price = sum(list(map(lambda x: x['price'], response.data)))
            total_receipt_price = sum(list(map(lambda x: x['receipt_price'], response.data)))
            response.data.append(OrderedDict())
            response.data.append(OrderedDict(month='Jami',
                                             not_receipt_price=total_price - total_receipt_price,
                                             receipt_price=total_receipt_price,
                                             price=total_price))
        except Exception as e:
            print(e)
        return response

    column_header = {
        'titles': [
            "Oy",
            "Cheksiz qilingan savdo",
            "Chek bilan qilingan savdo",
            "Umumiy",
        ],
        'column_width': [30, 50, 50, 50],
        'height': 50,
        'style': {
            'fill': {
                'fill_type': 'solid',
                'start_color': 'CCCCCC',
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
                'start_color': 'EEEEEE',
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
