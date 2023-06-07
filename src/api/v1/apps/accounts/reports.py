from collections import OrderedDict

from django.utils.encoding import escape_uri_path
from rest_framework import serializers
from drf_excel.mixins import XLSXFileMixin
from drf_excel.renderers import XLSXRenderer
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.apps.accounts.models import WorkerReport, WorkerReportMonth, CustomUser
from api.v1.apps.companies.enums import MONTHS
from api.v1.apps.accounts.permissions import IsDirector, IsManager


class WorkerReportSerializer(serializers.ModelSerializer):
    worker = serializers.StringRelatedField()
    creator = serializers.StringRelatedField()
    pharmacy = serializers.StringRelatedField()

    class Meta:
        model = WorkerReport
        fields = ['is_expense', 'report_date', 'price', 'creator', 'worker', 'created_at', 'pharmacy']


class WorkerReportMonthSerializer(serializers.ModelSerializer):
    worker = serializers.StringRelatedField()
    pharmacy = serializers.StringRelatedField()

    class Meta:
        model = WorkerReportMonth
        fields = ['worker', 'year', 'month', 'expense_price', 'income_price', 'pharmacy']


class WorkerReportMonthExcelSerializer(serializers.ModelSerializer):
    worker = serializers.StringRelatedField()
    pharmacy = serializers.StringRelatedField()

    class Meta:
        model = WorkerReportMonth
        fields = ['year', 'month', 'pharmacy', 'worker', 'income_price', 'expense_price']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['month'] = MONTHS[ret['month']]
        return ret


class WorkerReportMontAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = WorkerReportMonthSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['worker', 'year', 'month', 'pharmacy']

    def get_queryset(self):
        queryset = WorkerReportMonth.objects.filter(worker__director_id=self.request.user.director_id).order_by('month')
        return queryset.select_related('worker', 'pharmacy')


class WorkerReportMontExcelAPIView(XLSXFileMixin, WorkerReportMontAPIView):
    renderer_classes = (XLSXRenderer,)
    serializer_class = WorkerReportMonthExcelSerializer

    def get_filename(self, request=None, *args, **kwargs):
        year = request.query_params.get('year')
        worker_id = request.query_params.get('worker')
        try:
            worker = CustomUser.objects.get(id=worker_id)
        except CustomUser.DoesNotExist:
            return f'{year}_report.xlsx'
        return f'{year}_{"".join(str(worker).split())}_report.xlsx'

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        filename = escape_uri_path(self.get_filename(request=request, *args, **kwargs))
        response["content-disposition"] = f"attachment; filename={filename}"
        try:
            total_expense_price = sum(list(map(lambda x: x['expense_price'], response.data)))
            total_income_price = sum(list(map(lambda x: x['income_price'], response.data)))
            response.data.append(OrderedDict())
            response.data.append(OrderedDict(worker='Jami',
                                             expense_price=total_expense_price,
                                             income_price=total_income_price))
        except Exception as e:
            print(e)
        return response

    column_header = {
        'titles': [
            "Yil",
            "Oy",
            "Filial",
            "Xodim",
            "Olgan pul miqdori",
            "Bergan pul miqdori",
        ],
        'column_width': [10, 20, 60, 60, 30, 30],
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


class CustomPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        month_income_total_price = data['month_income_total_price']
        month_expense_total_price = data['month_expense_total_price']
        del data['month_income_total_price']
        del data['month_expense_total_price']
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('month_income_total_price', month_income_total_price),
            ('month_expense_total_price', month_expense_total_price),
            ('results', data['results'])
        ]))


class WorkerReportAPIView(ReadOnlyModelViewSet):
    pagination_class = CustomPageNumberPagination
    serializer_class = WorkerReportSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'report_date': ['month', 'year'],
        'worker': ['exact'],
        'pharmacy': ['exact'],
    }

    def get_queryset(self):
        queryset = WorkerReport.objects.filter(creator__director_id=self.request.user.director_id
                                               ).order_by('report_date')

        return queryset.select_related('pharmacy', 'creator', 'worker')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        month = request.query_params.get('report_date__month')
        year = request.query_params.get('report_date__year')
        worker = request.query_params.get('worker')
        pharmacy = request.query_params.get('pharmacy')
        month_income_total_price = 0
        month_expense_total_price = 0
        if month and year and worker and pharmacy:
            try:
                obj = WorkerReportMonth.objects.get(month=month, year=year, worker_id=worker, pharmacy_id=pharmacy)
                month_income_total_price = obj.income_price
                month_expense_total_price = obj.expense_price
            except WorkerReportMonth.DoesNotExist:
                pass

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        data = {
            'month_income_total_price': month_income_total_price,
            'month_expense_total_price': month_expense_total_price,
            'results': serializer.data
        }
        return self.get_paginated_response(data)
