from datetime import datetime

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.v1.pharmacies.services import get_worker_report_date
from api.v1.accounts.permissions import NotProjectOwner

from .models import RemainderShift


class RemainderAPIView(mixins.ListModelMixin, GenericViewSet):
    pagination_class = None
    permission_classes = [IsAuthenticated, NotProjectOwner]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pharmacy', 'report_date', 'shift']

    def list(self, request, *args, **kwargs):
        user = request.user

        if user.is_worker:
            return Response({'price': RemainderShift.objects.filter(shift=user.shift,
                                                                    pharmacy_id=user.pharmacy_id,
                                                                    report_date=get_worker_report_date(
                                                                        user.pharmacy.last_shift_end_hour))})

        try:
            pharmacy_id = int(request.GET['pharmacy_id'])
            report_date = datetime.strptime(request.GET['report_date'], '%Y-%m-%d').date()
            shift = int(request.GET['shift'])
            return Response({'price': RemainderShift.objects.filter(report_date=report_date,
                                                                    shift=shift,
                                                                    pharmacy_id=pharmacy_id)})
        except Exception as e:
            return Response(str(e))
