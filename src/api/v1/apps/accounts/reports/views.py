from collections import OrderedDict

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import WorkerReport, WorkerReportMonth
from ..permissions import IsDirector, IsManager


class WorkerReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerReport
        fields = ['is_expense', 'report_date', 'price', 'creator', 'worker', 'created_at']


class CustomPageNumberPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        total_month_price = data['total_month_price']
        del data['total_month_price']
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_month_price', total_month_price),
            ('results', data['results'])
        ]))


class WorkerReportAPIView(ReadOnlyModelViewSet):
    pagination_class = CustomPageNumberPagination
    serializer_class = WorkerReportSerializer
    permission_classes = [IsAuthenticated, (IsDirector | IsManager)]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'report_date': ['month', 'year'],
        'worker': ['exact']
    }

    def get_queryset(self):
        return WorkerReport.objects.filter(creator__director_id=self.request.user.director_id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        month = request.query_params.get('report_date__month')
        year = request.query_params.get('report_date__year')
        worker = request.query_params.get('worker')
        total_month_price = 0
        if month and year and worker:
            try:
                total_month_price = WorkerReportMonth.objects.get(month=month, year=year, worker_id=worker).price
            except WorkerReportMonth.DoesNotExist:
                total_month_price = 0

        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        data = {
            'total_month_price': total_month_price,
            'results': serializer.data
        }
        return self.get_paginated_response(data)
