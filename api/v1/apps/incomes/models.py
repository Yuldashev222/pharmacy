from django.db import models

from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.general.models import TransferMoneyType, AbstractIncomeExpense


class PharmacyIncome(AbstractIncomeExpense):
    to_firm, to_user = (None,) * 2

    to_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    is_transfer = models.BooleanField(default=True)
    transfer_type = models.ForeignKey(TransferMoneyType, on_delete=models.PROTECT,
                                      blank=True, null=True)

    def __str__(self):
        return f'{self.report.report_date} | {self.to_pharmacy}: {self.price}'


class PharmacyIncomeHistory(PharmacyIncome):
    pharmacy_income = models.ForeignKey(PharmacyIncome, on_delete=models.CASCADE)
    updater = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    updated_at = models.DateTimeField(auto_now_add=True)
