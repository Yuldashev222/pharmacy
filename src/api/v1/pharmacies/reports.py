from collections import OrderedDict
from rest_framework import serializers
from drf_excel.renderers import XLSXRenderer
from django.utils.encoding import escape_uri_path
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.accounts.permissions import IsDirector, IsManager
from .models import PharmacyReportByShift, Pharmacy


class PharmacyReportSerializer(serializers.ModelSerializer):
    worker = serializers.StringRelatedField()

    class Meta:
        model = PharmacyReportByShift
        exclude = [
            'expense_debt_repay_from_pharmacy',
            'expense_debt_from_pharmacy',
            'expense_pharmacy',
            'expense_firm',
        ]


class PharmacyReportAPIViewSet(ReadOnlyModelViewSet):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'pharmacy': ['exact'],
        'report_date': ['year', 'month'],
    }
    serializer_class = PharmacyReportSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = []
        obj = {}
        datas = []
        for i in serializer.data:
            report_date = i['report_date']
            del i['report_date']
            if report_date not in datas:
                if obj:
                    data.append(obj)
                    obj = {}
                datas.append(report_date)
                obj['report_date'] = report_date
                obj['shifts'] = []
            obj['shifts'].append(i)
        else:
            if obj:
                data.append(obj)
        return Response(data)

    def get_queryset(self):
        user = self.request.user
        queryset = PharmacyReportByShift.objects.filter(pharmacy__director_id=user.director_id).select_related('worker')
        return queryset.order_by('report_date', 'shift')


class PharmacyReportExcelSerializer(serializers.ModelSerializer):
    pharmacy = serializers.StringRelatedField()
    total_income_shift = serializers.SerializerMethodField()
    total_income_day = serializers.SerializerMethodField()
    not_receipt_price = serializers.SerializerMethodField()
    total_income = serializers.SerializerMethodField()

    def get_total_income_shift(self, val):
        return 0

    def get_total_income(self, val):
        return 0

    def get_total_income_day(self, val):
        return 0

    def get_not_receipt_price(self, val):
        return 0

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['total_income_shift'] = ret['not_transfer_income'] + ret['transfer_income']
        return ret

    class Meta:
        model = PharmacyReportByShift
        fields = [
            'pharmacy', 'report_date', 'shift', 'not_transfer_income', 'transfer_income', 'debt_income',
            'total_income_shift', 'total_income', 'total_expense', 'remainder', 'total_income_day',
            'not_receipt_price', 'receipt_price',
        ]


class PharmacyReportExcelAPIViewSet(PharmacyReportAPIViewSet):
    serializer_class = PharmacyReportExcelSerializer
    renderer_classes = (XLSXRenderer,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_filename(self, request=None, *args, **kwargs):
        year = request.query_params.get('report_date__year')
        month = request.query_params.get('report_date__month')
        pharmacy_id = request.query_params.get('pharmacy')
        try:
            obj = Pharmacy.objects.get(id=pharmacy_id)
        except Pharmacy.DoesNotExist:
            return f'{year}_{month}_pharmacy.xlsx'
        return f'{year}_{month}_{"".join(obj.name.split())}.xlsx'

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        filename = escape_uri_path(self.get_filename(request=request, *args, **kwargs))
        response["content-disposition"] = f"attachment; filename={filename}"

        data = []
        obj = OrderedDict()
        datas = []
        for i in response.data:
            report_date = i['report_date']
            del i['report_date']
            if report_date not in datas:
                if obj:
                    obj['total_income_day'] = sum(
                        list(map(lambda x: x['not_transfer_income'] + x['transfer_income'], obj['shifts'])))

                    obj['receipt_price'] = sum(
                        list(map(lambda x: x['receipt_price'], obj['shifts'])))

                    obj['not_receipt_price'] = obj['total_income_day'] - obj['receipt_price']

                    data.append(obj)
                    obj = OrderedDict()
                datas.append(report_date)
                obj['report_date'] = report_date
                obj['pharmacy'] = i['pharmacy']
                obj['shifts'] = []

            obj['shifts'].append(i)
        else:
            if obj:
                data.append(obj)
        response.data = data
        try:
            total_not_transfer_income = sum(list(map(lambda x: x['not_transfer_income'], response.data)))
            total_transfer_income = sum(list(map(lambda x: x['transfer_income'], response.data)))
            total_debt_income = sum(list(map(lambda x: x['debt_income'], response.data)))
            total_income_shift = sum(list(map(lambda x: x['total_income_shift'], response.data)))
            total_expense = sum(list(map(lambda x: x['total_expense'], response.data)))
            total_remainder = sum(list(map(lambda x: x['total_remainder'], response.data)))
            total_income = sum(list(map(lambda x: x['total_income'], response.data)))
            total_not_receipt_price = sum(list(map(lambda x: x['not_receipt_price'], response.data)))
            total_receipt_price = sum(list(map(lambda x: x['receipt_price'], response.data)))
            response.data.append(OrderedDict())
            response.data.append(OrderedDict(shift='Jami',
                                             not_transfer_income=total_not_transfer_income,
                                             transfer_income=total_transfer_income,
                                             debt_income=total_debt_income,
                                             total_income_shift=total_income_shift,
                                             total_expense=total_expense,
                                             total_remainder=total_remainder,
                                             total_income=total_income,
                                             not_receipt_price=total_not_receipt_price,
                                             receipt_price=total_receipt_price))
        except Exception as e:
            print(e)
        return response

    column_header = {
        'titles': [
            'pharmacy',
            'report_date',
            'shift',
            'not_transfer_income',
            'transfer_income',
            'debt_income',
            'total_income_shift',
            'total_income',
            'total_expense',
            'remainder',
            'total_income_day',
            'not_receipt_price',
            'receipt_price',
        ],
        'column_width': [60, 30, 10, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30],
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
