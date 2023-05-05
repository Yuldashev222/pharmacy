from django.db import models

from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.general.models import TransferMoneyType, AbstractIncomeExpense


class PharmacyIncome(AbstractIncomeExpense):
    income_expense_type = None

    to_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    is_transfer = models.BooleanField(default=True)
    transfer_type = models.ForeignKey(TransferMoneyType, on_delete=models.PROTECT,
                                      blank=True, null=True)

    def __str__(self):
        return f'{self.to_pharmacy}: {self.price}'


class PharmacyIncomeHistory(PharmacyIncome):
    pharmacy_income = models.ForeignKey(PharmacyIncome, on_delete=models.CASCADE,
                                        related_name='pharmacy_incomes_history')
