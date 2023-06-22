from collections import OrderedDict
from datetime import timedelta

from rest_framework import serializers, filters
from django.db.models import Sum
from drf_excel.renderers import XLSXRenderer
from django.utils.encoding import escape_uri_path
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.firms.models import FirmReport, FirmDebtByDate, FirmDebtByMonth, Firm
from api.v1.accounts.permissions import IsDirector, IsManager


class FirmReportSerializer(serializers.ModelSerializer):
    pharmacy_name = serializers.StringRelatedField(source='pharmacy')
    creator_name = serializers.StringRelatedField(source='creator')

    class Meta:
        model = FirmReport
        exclude = ['expense', 'income', 'return_product']


class FirmDebtByMonthSerializer(serializers.ModelSerializer):
    firm_name = serializers.StringRelatedField(source='firm')
    pharmacy_name = serializers.StringRelatedField(source='pharmacy')

    class Meta:
        model = FirmDebtByMonth
        fields = '__all__'


class FirmDebtByDateSerializer(serializers.ModelSerializer):
    firm_name = serializers.StringRelatedField(source='firm')

    class Meta:
        model = FirmDebtByDate
        fields = '__all__'


class FirmDebtByDateAPIView(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    serializer_class = FirmDebtByDateSerializer
    filterset_fields = ['firm', 'report_date']
    search_fields = ['firm__name']

    def get_queryset(self):
        return FirmDebtByDate.objects.filter(firm__director_id=self.request.user.director_id).select_related(
            'firm').order_by('-report_date')


class FirmDebtByMonthAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = FirmDebtByMonthSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['year', 'firm', 'pharmacy']

    def get_queryset(self):
        return FirmDebtByMonth.objects.filter(firm__director_id=self.request.user.director_id
                                              ).select_related('firm', 'pharmacy').order_by('month')


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
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    pagination_class = CustomPageNumberPagination
    serializer_class = FirmReportSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'report_date': ['gte', 'lte', 'month', 'year'],
        'pharmacy': ['exact'],
        'firm': ['exact'],
        'is_expense': ['exact'],
    }

    def get_queryset(self):
        user = self.request.user
        return FirmReport.objects.filter(creator__director_id=user.director_id
                                         ).select_related('creator', 'pharmacy').order_by('report_date', 'created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        start_date = request.query_params.get('report_date__gte')
        firm_id = request.query_params.get('firm')
        transfer_debt_in_start_date = 0
        not_transfer_debt_in_start_date = 0
        if start_date and firm_id:
            try:
                obj = FirmDebtByDate.objects.filter(report_date__lt=start_date,
                                                    firm_id=firm_id
                                                    ).order_by('-report_date').first()
                transfer_debt_in_start_date = obj.transfer_debt
                not_transfer_debt_in_start_date = obj.not_transfer_debt
            except AttributeError:
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


class FirmReportExcelSerializer(serializers.ModelSerializer):
    pharmacy = serializers.StringRelatedField()
    creator = serializers.StringRelatedField()

    class Meta:
        model = FirmReport
        fields = [
            'report_date', 'created_at', 'pharmacy', 'creator', 'verified_firm_worker_name', 'verified_phone_number',
            'is_expense', 'price', 'is_transfer', 'id'
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        is_expense = ret['is_expense']
        is_transfer = ret['is_transfer']
        price = ret['price']
        if is_expense and is_transfer:
            ret['is_transfer'] = price
            ret['is_expense'] = '-'
            ret['price'] = '-'
            ret['id'] = '-'
        elif not (is_expense or is_transfer):
            ret['is_transfer'] = '-'
            ret['is_expense'] = '-'
            ret['id'] = '-'
        elif is_expense:
            ret['is_transfer'] = '-'
            ret['is_expense'] = price
            ret['price'] = '-'
            ret['id'] = '-'
        elif is_transfer:
            ret['is_transfer'] = '-'
            ret['is_expense'] = '-'
            ret['price'] = '-'
            ret['id'] = price
        return ret


class FirmReportExcelAPIView(FirmReportAPIView):
    pagination_class = None
    serializer_class = FirmReportExcelSerializer
    renderer_classes = (XLSXRenderer,)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_filename(self, request=None, *args, **kwargs):
        firm_id = request.query_params.get('firm')
        try:
            obj = Firm.objects.get(id=firm_id)
        except:
            return 'firm_report.xlsx'
        return f'{obj.name}_report.xlsx'

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        filename = escape_uri_path(self.get_filename(request=request, *args, **kwargs))
        response["content-disposition"] = f"attachment; filename={filename}"

        end_date = request.query_params.get('report_date__lte')
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

        try:
            total_is_expense_column = sum(
                list(map(lambda x: x['is_expense'] if isinstance(x['is_expense'], int) else 0, response.data)))
            total_price_column = sum(
                list(map(lambda x: x['price'] if isinstance(x['price'], int) else 0, response.data)))
            total_is_transfer_column = sum(
                list(map(lambda x: x['is_transfer'] if isinstance(x['is_transfer'], int) else 0, response.data)))
            total_id_column = sum(list(map(lambda x: x['id'] if isinstance(x['id'], int) else 0, response.data)))
            response.data.append(OrderedDict())
            response.data.append(OrderedDict(verified_phone_number='Jami',
                                             is_expense=total_is_expense_column,
                                             price=total_price_column,
                                             is_transfer=total_is_transfer_column,
                                             id=total_id_column))
            response.data.append(OrderedDict())
            response.data.append(OrderedDict(verified_phone_number=f'{start_date} xolatiga qarz miqdori:',
                                             is_expense=not_transfer_debt_in_start_date + transfer_debt_in_start_date))

            sm = not_transfer_debt_in_start_date - total_is_expense_column + total_price_column + transfer_debt_in_start_date - total_is_transfer_column + total_id_column
            response.data.append(OrderedDict(verified_phone_number=f'{end_date} xolatiga qarz miqdori:',
                                             is_expense=sm))

        except Exception as e:
            print(e)
        return response

    column_header = {
        'titles': [
            'Sana',
            'Qo\'shilgan sana',
            'Filial',
            'Xodim',
            'Firma xodimi',
            'Tasdiqlangan tel raqam',
            'naqt chiqim',
            'naqt kirim',
            'naqtsiz chiqim',
            'naqtsiz kirim',
        ],
        'column_width': [30, 30, 30, 30, 30, 30, 30, 30, 30, 30],
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
