from django.db import models

from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.general.models import TransferMoneyType, AbstractIncomeExpense


class PharmacyExpense(AbstractIncomeExpense):
    to_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
                                null=True, blank=True,
                                related_name='pharmacy_expenses')
    from_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)

    def __str__(self):
        return f'{self.report.report_date} | {self.from_pharmacy}: {self.price}'


class UserExpense(AbstractIncomeExpense):  # firmaniki alohida
    from_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,
                                  related_name='expenses')

    is_transfer = models.BooleanField(default=True)
    transfer_type = models.ForeignKey(TransferMoneyType, on_delete=models.PROTECT,
                                      blank=True, null=True)

    def __str__(self):
        return f'{self.report.report_date} | {self.from_user}: {self.price}'


class PharmacyExpenseHistory(PharmacyExpense):
    pharmacy_expense = models.ForeignKey(PharmacyExpense, on_delete=models.CASCADE,
                                         related_name='pharmacy_expenses_history')

    updater = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,
                                related_name='pharmacy_expenses_history')
    updated_at = models.DateTimeField(auto_now_add=True)


class UserExpenseHistory(UserExpense):
    user_expense = models.ForeignKey(UserExpense, on_delete=models.CASCADE,
                                     related_name='user_expenses_history')
    updater = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True,
                                related_name='user_expenses_history')
    updated_at = models.DateTimeField(auto_now_add=True)
