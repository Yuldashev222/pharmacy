from django.db.models import Sum
from datetime import datetime
from api.v1.apps.firms.models import FirmExpense
from api.v1.apps.debts.models import DebtToPharmacy, DebtRepayFromPharmacy, DebtRepayToPharmacy, DebtFromPharmacy
from api.v1.apps.incomes.models import PharmacyIncome
from api.v1.apps.expenses.models import UserExpense, PharmacyExpense


def pharmacy_logo_upload_location(obj, logo):
    return f'pharmacies/{obj.name[:200]}/logos/{logo}'


def get_remainder(report_date, shift, pharmacy_id):
    try:
        report_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        shift = int(shift)
        pharmacy_id = int(pharmacy_id)
    except Exception as e:
        return str(e)

    shift -= 1
    if shift < 1:
        return 0

    d = {'report_date': report_date, 'shift': shift, 'transfer_type_id': 1}

    income1 = DebtToPharmacy.objects.filter(
        **d, to_pharmacy_id=pharmacy_id).aggregate(p=Sum('price'))['p']
    income2 = DebtRepayToPharmacy.objects.filter(
        **d, from_debt__from_pharmacy_id=pharmacy_id).aggregate(p=Sum('price'))['p']
    income3 = UserExpense.objects.filter(
        **d, to_pharmacy_id=pharmacy_id).aggregate(p=Sum('price'))['p']
    income4 = PharmacyIncome.objects.filter(
        **d, to_user__isnull=True, to_pharmacy_id=pharmacy_id).aggregate(p=Sum('price'))['p']

    total_income = sum([
        0 if income1 is None else income1,
        0 if income2 is None else income2,
        0 if income3 is None else income3,
        0 if income4 is None else income4,
    ])

    expense1 = DebtFromPharmacy.objects.filter(
        **d, from_pharmacy_id=pharmacy_id).aggregate(p=Sum('price'))['p']
    expense2 = DebtRepayFromPharmacy.objects.filter(
        **d, to_debt__to_pharmacy_id=pharmacy_id).aggregate(p=Sum('price'))['p']
    expense3 = PharmacyExpense.objects.filter(
        **d, from_pharmacy_id=pharmacy_id).aggregate(p=Sum('price'))['p']
    expense4 = FirmExpense.objects.filter(
        **d, from_user__isnull=True, from_pharmacy_id=pharmacy_id).aggregate(p=Sum('price'))['p']

    total_expense = sum([
        0 if expense1 is None else expense1,
        0 if expense2 is None else expense2,
        0 if expense3 is None else expense3,
        0 if expense4 is None else expense4,
    ])
    return total_income - total_expense
