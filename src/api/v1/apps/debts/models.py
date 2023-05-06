from django.db import models

from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.general.models import AbstractIncomeExpense, TransferMoneyType


class DebtToPharmacy(AbstractIncomeExpense):  # aptekaga qarz berdi
    from_who = models.CharField(max_length=500)
    to_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    is_paid = models.BooleanField(default=False)

    def repaid_debt(self):
        return self.debtrepayfrompharmacy_set.aggregate(total=models.Sum('price'))['total']

    def __str__(self):
        return self.from_who


class DebtRepayFromPharmacy(AbstractIncomeExpense):  # apteka qarzini qaytardi
    to_debt = models.ForeignKey(DebtToPharmacy, on_delete=models.PROTECT)
    from_user = models.ForeignKey(CustomUser, on_delete=models.PROTECT,
                                  related_name='debt_repays', blank=True, null=True)

    def __str__(self):
        return str(self.to_debt)


class DebtFromPharmacy(AbstractIncomeExpense):  # apteka qarz berdi
    is_paid = models.BooleanField(default=False)
    is_client = models.BooleanField(default=True)
    from_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    to_who = models.CharField(max_length=500)

    def __str__(self):
        return str(self.from_pharmacy)

    def repaid_debt(self):
        return self.debtrepaytopharmacy_set.aggregate(total=models.Sum('price'))['total']


class DebtRepayToPharmacy(AbstractIncomeExpense):  # aptekaga qarzini qaytardi
    from_debt = models.ForeignKey(DebtFromPharmacy, on_delete=models.PROTECT)
