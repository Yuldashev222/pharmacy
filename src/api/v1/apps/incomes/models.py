from django.db import models

from api.v1.apps.companies.models import TransferMoneyType, AbstractIncomeExpense


class PharmacyIncome(AbstractIncomeExpense):
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    to_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT,
        related_name='pharmacy_incomes', blank=True, null=True
    )

    def __str__(self):
        return f'{self.to_pharmacy}: {self.price}'
