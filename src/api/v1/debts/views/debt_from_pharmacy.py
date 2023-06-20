from collections import OrderedDict
from rest_framework import filters, serializers
from drf_excel.renderers import XLSXRenderer
from django.utils.encoding import escape_uri_path
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from api.v1.pharmacies.models import Pharmacy
from api.v1.pharmacies.services import get_worker_report_date
from api.v1.accounts.permissions import NotProjectOwner
from api.v1.companies.permissions import WorkerTodayObject

from ..models import DebtFromPharmacy, DebtRepayToPharmacy
from ..serializers import debt_from_pharmacy, debt_repay_to_pharmacy


class DebtFromPharmacyAPIView(ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        'is_paid': ['exact'],
        'from_pharmacy': ['exact'],
        'report_date': ['exact', 'year', 'month'],
        'shift': ['exact'],
        'is_client': ['exact']
    }
    search_fields = ['to_who', 'desc']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        user = self.request.user
        if user.is_authenticated and user.is_worker and self.action not in ['list', 'retrieve']:  # last
            permission_classes += [WorkerTodayObject]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        data = {'creator_id': user.id}
        if user.is_worker:
            data['report_date'] = get_worker_report_date(user.pharmacy.last_shift_end_hour)
            data['from_pharmacy_id'] = user.pharmacy_id
            data['shift'] = user.shift
        serializer.save(**data)

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and user.is_worker:
            return debt_from_pharmacy.WorkerDebtFromPharmacySerializer
        return debt_from_pharmacy.DirectorManagerDebtFromPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy_id=user.pharmacy_id)
        else:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy__director_id=user.director_id)
        return queryset.select_related('creator', 'from_pharmacy', 'transfer_type').order_by('-report_date',
                                                                                             '-created_at')


class DebtFromPharmacyExcelSerializer(serializers.ModelSerializer):
    creator = serializers.StringRelatedField()

    class Meta:
        model = DebtFromPharmacy
        fields = ['report_date', 'created_at', 'creator', 'to_who', 'price', 'id', 'remaining_debt']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['id'] = ret['price'] - ret['remaining_debt']
        return ret


class DebtFromPharmacyExcelAPIView(DebtFromPharmacyAPIView):
    pagination_class = None
    renderer_classes = (XLSXRenderer,)

    def get_serializer_class(self):
        return DebtFromPharmacyExcelSerializer

    def get_filename(self, request=None, *args, **kwargs):
        pharmacy_id = request.query_params.get('from_pharmacy')
        try:
            obj = Pharmacy.objects.get(id=pharmacy_id)
        except:
            return 'pharmacy_to_debts.xlsx'
        return f'{obj.name}_to_debts.xlsx'

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        filename = escape_uri_path(self.get_filename(request=request, *args, **kwargs))
        response["content-disposition"] = f"attachment; filename={filename}"
        try:
            total_debts = sum(list(map(lambda x: x['price'], response.data)))
            total_broken_debts = sum(list(map(lambda x: x['id'], response.data)))
            total_remaining_debts = sum(list(map(lambda x: x['remaining_debt'], response.data)))
            response.data.append(OrderedDict())
            response.data.append(OrderedDict(to_who='Jami',
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
            'Kim qarz oldi',
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


class TodayDebtFromPharmacyAPIView(DebtFromPharmacyAPIView):
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy_id=user.pharmacy_id,
                                                       shift=user.shift,
                                                       report_date=get_worker_report_date(
                                                           user.pharmacy.last_shift_end_hour))
        else:
            queryset = DebtFromPharmacy.objects.filter(from_pharmacy__director_id=user.director_id)
        return queryset.select_related('creator', 'from_pharmacy', 'transfer_type').order_by('-report_date',
                                                                                             '-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})


class DebtRepayToPharmacyAPIView(ModelViewSet):
    pagination_class = None
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['report_date', 'shift', 'from_debt__is_client', 'from_debt__from_pharmacy']

    def get_permissions(self):
        permission_classes = [IsAuthenticated, NotProjectOwner]
        user = self.request.user
        if user.is_authenticated and user.is_worker and self.action not in ['list', 'retrieve']:
            permission_classes += [WorkerTodayObject]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        data = {'creator_id': user.id}
        if user.is_worker:
            data['report_date'] = get_worker_report_date(user.pharmacy.last_shift_end_hour)
            data['shift'] = user.shift
        serializer.save(**data)

    def perform_destroy(self, instance):
        from_debt = instance.from_debt
        from_debt.remaining_debt += instance.price
        if from_debt.remaining_debt > 0:
            from_debt.is_paid = False
        from_debt.save()
        instance.delete()

    def get_serializer_class(self):
        user = self.request.user
        if user.is_authenticated and user.is_worker:
            return debt_repay_to_pharmacy.WorkerDebtRepayToPharmacySerializer
        return debt_repay_to_pharmacy.DirectorManagerDebtRepayToPharmacySerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_worker:
            queryset = DebtRepayToPharmacy.objects.filter(from_debt__from_pharmacy_id=user.pharmacy_id,
                                                          shift=user.shift,
                                                          report_date=get_worker_report_date(
                                                              user.pharmacy.last_shift_end_hour))
        else:
            queryset = DebtRepayToPharmacy.objects.filter(from_debt__from_pharmacy__director_id=user.director_id)
        return queryset.select_related('creator', 'from_debt', 'transfer_type').order_by('-report_date',
                                                                                         '-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response({'results': serializer.data})
