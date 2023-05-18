from django.db.models import Sum

from api.v1.apps.firms.models import FirmExpense
from api.v1.apps.debts.models import DebtToPharmacy, DebtRepayFromPharmacy, DebtRepayToPharmacy, DebtFromPharmacy
from api.v1.apps.incomes.models import PharmacyIncome
from api.v1.apps.expenses.models import UserExpense, PharmacyExpense


def pharmacy_logo_upload_location(obj, logo):
    return f'pharmacies/{obj.name[:200]}/logos/{logo}'


def get_remainder(report_date, shift, pharmacy_id):
    shift -= 1
    if shift < 1:
        return 0

    d = {'report_date': report_date, 'shift': shift, 'transfer_type_id': 1}
    total_income = sum([
        DebtToPharmacy.objects.filter(**d, to_pharmacy_id=pharmacy_id).aggregate(
            p=Sum('price')
        )['p'],
        DebtRepayToPharmacy.objects.filter(**d, from_debt__from_pharmacy_id=pharmacy_id).aggregate(
            p=Sum('price')
        )['p'],
        UserExpense.objects.filter(**d, to_pharmacy_id=pharmacy_id).aggregate(
            p=Sum('price')
        )['p'],
        PharmacyIncome.objects.filter(**d, to_user__isnull=True, to_pharmacy_id=pharmacy_id).aggregate(
            p=Sum('price')
        )['p'],
    ])
    total_expense = sum([
        DebtFromPharmacy.objects.filter(**d, from_pharmacy_id=pharmacy_id).aggregate(
            p=Sum('price')
        )['p'],
        DebtRepayFromPharmacy.objects.filter(**d, to_debt__to_pharmacy_id=pharmacy_id).aggregate(
            p=Sum('price')
        )['p'],
        PharmacyExpense.objects.filter(**d, from_pharmacy_id=pharmacy_id).aggregate(
            p=Sum('price')
        )['p'],
        FirmExpense.objects.filter(**d, from_user__isnull=True, from_pharmacy_id=pharmacy_id).aggregate(
            p=Sum('price')
        )['p'],
    ])
    return total_income - total_expense
