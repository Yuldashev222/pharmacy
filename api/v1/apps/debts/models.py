from django.db import models

from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.general.models import AbstractIncomeExpense


class DebtToPharmacy(AbstractIncomeExpense):  # aptekaga qarz berdi
    income_expense_type = None

    from_who = models.CharField(max_length=500)
    to_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)

    def repaid_debt(self):
        return self.debtrepayfrompharmacy_set.aggregate(total=models.Sum('price'))['total']

    def __str__(self):
        return self.from_who


class DebtRepayFromPharmacy(AbstractIncomeExpense):  # apteka qarzni qaytardi
    income_expense_type = None

    to_debt = models.ForeignKey(DebtToPharmacy, on_delete=models.PROTECT)
    from_pharmacy = models.BooleanField(default=True)  # desc   select  # last

    def __str__(self):
        return str(self.to_debt)


class DebtFromPharmacy(AbstractIncomeExpense):  # apteka qarz bedi
    income_expense_type = None

    is_paid = models.BooleanField(default=False)
    is_client = models.BooleanField(default=True)
    from_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    to_who = models.CharField(max_length=500)

    def __str__(self):
        return str(self.from_pharmacy)

    def repaid_debt(self):
        return self.debtrepaytopharmacy_set.aggregate(total=models.Sum('price'))['total']


class DebtRepayToPharmacy(AbstractIncomeExpense):  # aptekaga qarzini qaytardi
    income_expense_type = None

    from_debt = models.ForeignKey(DebtFromPharmacy, on_delete=models.PROTECT)
