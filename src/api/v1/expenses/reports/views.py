from collections import OrderedDict

from django.utils.encoding import escape_uri_path
from drf_excel.renderers import XLSXRenderer
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.companies.enums import MONTHS
from api.v1.pharmacies.models import Pharmacy
from api.v1.accounts.permissions import IsDirector, IsManager

from .models import ExpenseReportMonth
from ..models import PharmacyExpense


class CustomPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        total_month_price = data['total_month_price']
        del data['total_month_price']
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_month_price', total_month_price),
            ('results', data['results'])
        ]))


class ExpenseSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()
    expense_type = serializers.StringRelatedField()
    from_pharmacy = serializers.StringRelatedField()

    class Meta:
        model = PharmacyExpense
        fields = ['creator', 'expense_type', 'from_pharmacy', 'price', 'created_at', 'report_date', 'second_name']


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
        queryset = PharmacyExpense.objects.filter(from_pharmacy__director_id=user.director_id
                                                  ).select_related('creator',
                                                                   'expense_type',
                                                                   'from_pharmacy'
                                                                   ).order_by('report_date')
        return queryset


class ExpenseExcelSerializer(ExpenseSerializer):
    class Meta:
        model = PharmacyExpense
        fields = ['report_date', 'created_at', 'creator', 'expense_type', 'from_pharmacy', 'second_name', 'price']


class ExpenseExcelAPIView(ExpenseAPIView):
    pagination_class = None
    serializer_class = ExpenseExcelSerializer
    renderer_classes = (XLSXRenderer,)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        filename = escape_uri_path(self.get_filename(request=request, *args, **kwargs))
        response["content-disposition"] = f"attachment; filename={filename}"

        month = request.query_params.get('report_date__month')
        year = request.query_params.get('report_date__year')
        pharmacy = request.query_params.get('from_pharmacy')
        expense_type = request.query_params.get('expense_type')
        if month and year and pharmacy:
            try:
                if expense_type:
                    total_month_price = ExpenseReportMonth.objects.get(month=month,
                                                                       year=year,
                                                                       pharmacy_id=pharmacy,
                                                                       expense_type_id=expense_type).price
                else:
                    total_month_price = ExpenseReportMonth.objects.get(month=month,
                                                                       year=year,
                                                                       pharmacy_id=pharmacy).price

                response.data.append(OrderedDict())
                response.data.append(OrderedDict(second_name='Jami', price=total_month_price))
            except Exception as e:
                print(e)

        return response

    def get_filename(self, request=None, *args, **kwargs):
        year = request.query_params.get('report_date__year')
        month = request.query_params.get('report_date__month')
        pharmacy = request.query_params.get('from_pharmacy')
        try:
            pharmacy = Pharmacy.objects.get(id=pharmacy)
            month = int(month)
            return f'{year}_{MONTHS[month]}_{"".join(str(pharmacy).split())}_expense_report.xlsx'
        except Exception as e:
            print(e)
        return f'{year}_expense_report.xlsx'

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    column_header = {
        'titles': [
            "Hisobot sanasi",
            "Qo'shilgan sanasi",
            "Yaratuvchi xodim",
            "Chiqim turi",
            "Filial",
            "Nomi",
            "Miqdor",
        ],
        'column_width': [30, 30, 60, 60, 60, 60, 60],
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
