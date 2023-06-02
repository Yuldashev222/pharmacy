from collections import OrderedDict
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from ..models import WorkerReport, WorkerReportMonth
from ..permissions import IsDirector, IsManager


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


class WorkerReportMontAPIView(ReadOnlyModelViewSet):
    pagination_class = None
    serializer_class = WorkerReportMonthSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['worker', 'year', 'month', 'pharmacy']

    def get_queryset(self):
        queryset = WorkerReportMonth.objects.filter(worker__director_id=self.request.user.director_id).order_by('month')
        return queryset.select_related('worker', 'pharmacy')


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
        queryset = WorkerReport.objects.filter(creator__director_id=self.request.user.director_id).order_by('report_date')
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
