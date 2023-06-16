from collections import OrderedDict

from django.utils.encoding import escape_uri_path
from drf_excel.renderers import XLSXRenderer
from rest_framework import filters, serializers
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.pharmacies.models import Pharmacy
from api.v1.pharmacies.services import get_worker_report_date
from api.v1.accounts.permissions import NotProjectOwner
from api.v1.companies.permissions import WorkerTodayObject

from ..models import DebtToPharmacy, DebtRepayFromPharmacy
from ..serializers import debt_to_pharmacy, debt_repay_from_pharmacy


class DebtToPharmacyAPIView(ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'is_paid': ['exact'],
        'report_date': ['exact', 'year', 'month'],
        'shift': ['exact'],
        'to_pharmacy': ['exact']
    }
    search_fields = ['from_who', 'desc']

    def perform_create(self, serializer):
        user = self.request.user
        data = {'creator_id': user.id}
        if user.is_worker:
            data['report_date'] = get_worker_report_date(user.pharmacy.last_shift_end_hour)
            data['to_pharmacy_id'] = user.pharmacy_id
            data['shift'] = user.shift
        serializer.save(**data)

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.request.user.is_worker and self.action not in ['list', 'retrieve']:
            permission_classes += [WorkerTodayObject]  # last
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return debt_to_pharmacy.WorkerDebtToPharmacySerializer
        return debt_to_pharmacy.DirectorManagerDebtToPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtToPharmacy.objects.filter(to_pharmacy_id=user.pharmacy_id, is_paid=False)
        else:
            queryset = DebtToPharmacy.objects.filter(to_pharmacy__director_id=user.director_id)
        queryset = queryset.exclude(to_firm_expense__isnull=False,
                                    to_firm_expense__is_verified=False).select_related('creator',
                                                                                       'to_pharmacy',
                                                                                       'transfer_type'
                                                                                       ).order_by('-created_at')
        return queryset


class DebtToPharmacyExcelSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()

    class Meta:
        model = DebtToPharmacy
        fields = ['report_date', 'created_at', 'creator', 'from_who', 'price', 'id', 'remaining_debt']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = ret['price'] - ret['remaining_debt']
        return ret


class DebtToPharmacyExcelAPIView(DebtToPharmacyAPIView):
    pagination_class = None
    renderer_classes = (XLSXRenderer,)

    def get_serializer_class(self):
        return DebtToPharmacyExcelSerializer

    def get_filename(self, request=None, *args, **kwargs):
        pharmacy_id = request.query_params.get('to_pharmacy')
        try:
            obj = Pharmacy.objects.get(id=pharmacy_id)
        except:
            return 'pharmacy_debts.xlsx'
        return f'{obj.name}_debts.xlsx'

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        filename = escape_uri_path(self.get_filename(request=request, *args, **kwargs))
        response["content-disposition"] = f"attachment; filename={filename}"
        try:
            total_debts = sum(list(map(lambda x: x['price'], response.data)))
            total_broken_debts = sum(list(map(lambda x: x['id'], response.data)))
            total_remaining_debts = sum(list(map(lambda x: x['remaining_debt'], response.data)))
            response.data.append(OrderedDict())
            response.data.append(OrderedDict(from_who='Jami',
                                             price=total_debts,
                                             id=total_broken_debts,
                                             remaining_debt=total_remaining_debts))
        except Exception as e:
            print(e)
        return response

    column_header = {
        'titles': [
            'Sana',
            'Qo\'shilgan sana',
            'Xodim',
            'Kimdan qarz olindi',
            'Qarz miqdori',
            'Uzilgan qarz miqdori',
            'Qolgan qarz miqdori',
        ],
        'column_width': [20, 30, 50, 50, 30, 30, 30],
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



class TodayDebtToPharmacyAPIView(DebtToPharmacyAPIView):
    pagination_class = None

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})


class DebtRepayFromPharmacyAPIView(ModelViewSet):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'to_debt__to_pharmacy']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        if self.request.user.is_worker and self.action not in ['list', 'retrieve']:
            permission_classes += [WorkerTodayObject]
        return [permission() for permission in permission_classes]

    def perform_destroy(self, instance):
        to_debt = instance.to_debt
        to_debt.remaining_debt += instance.price
        if to_debt.remaining_debt > 0:
            to_debt.is_paid = False
        to_debt.save()
        instance.delete()

    def perform_create(self, serializer):
        user = self.request.user
        data = {'creator_id': user.id}
        if user.is_worker:
            data['shift'] = user.shift
            data['report_date'] = get_worker_report_date(user.pharmacy.last_shift_end_hour)
        serializer.save(**data)

    def get_serializer_class(self):
        if self.request.user.is_worker:
            return debt_repay_from_pharmacy.WorkerDebtRepayFromPharmacySerializer
        return debt_repay_from_pharmacy.DirectorManagerDebtRepayFromPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtRepayFromPharmacy.objects.filter(to_debt__to_pharmacy_id=user.pharmacy_id,
                                                            shift=user.shift,
                                                            report_date=get_worker_report_date(
                                                                user.pharmacy.last_shift_end_hour))
        else:
            queryset = DebtRepayFromPharmacy.objects.filter(to_debt__to_pharmacy__director_id=user.director_id)
        return queryset.select_related('creator', 'from_user', 'transfer_type', 'to_debt').order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})
