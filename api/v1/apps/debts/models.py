from django.db import models

from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.general.models import AbstractIncomeExpense


class DebtIncome(AbstractIncomeExpense):
    income_expense_type, to_firm = (None,) * 2

    is_paid = models.BooleanField(default=False)
    desc = models.CharField(max_length=500)

    # select
    to_user = models.ForeignKey(CustomUser, on_delete=models.PROTECT,
                                blank=True, null=True)
    to_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT,
                                    blank=True, null=True)
    # ------


class DebtExpense(AbstractIncomeExpense):
    income_expense_type, to_firm, to_user = (None,) * 3

    to_debt = models.ForeignKey(DebtIncome, on_delete=models.PROTECT)

    # select
    from_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT,
                                      blank=True, null=True)
    from_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
                                  null=True, blank=True)
    desc = models.CharField(max_length=500, blank=True)
    # ------
