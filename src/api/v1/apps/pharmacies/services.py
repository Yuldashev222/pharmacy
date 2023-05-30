from django.db.models import Sum
from datetime import datetime
from api.v1.apps.firms.models import FirmExpense
from api.v1.apps.debts.models import DebtToPharmacy, DebtRepayFromPharmacy, DebtRepayToPharmacy, DebtFromPharmacy
from api.v1.apps.incomes.models import PharmacyIncome
from api.v1.apps.expenses.models import UserExpense, PharmacyExpense


def pharmacy_logo_upload_location(obj, logo):
    return f'pharmacies/{obj.name[:200]}/logos/{logo}'

