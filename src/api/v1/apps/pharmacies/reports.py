from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated

from api.v1.apps.accounts.permissions import IsDirector, IsManager
from .models import PharmacyReportByShift


class PharmacyReportSerializer(serializers.ModelSerializer):

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
            print()
            report_date = i['report_date']
            del i['report_date']
            if report_date not in datas:
                if obj:
                    print(obj)
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
        queryset = PharmacyReportByShift.objects.filter(pharmacy__director_id=user.director_id)
        return queryset.order_by('report_date', 'shift')
