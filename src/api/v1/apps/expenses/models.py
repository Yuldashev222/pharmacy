from django.db import models

from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.general.models import AbstractIncomeExpense, ExpenseType


class UserExpense(AbstractIncomeExpense):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    from_user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='from_user_expenses')
    to_user = models.ForeignKey(CustomUser, on_delete=models.PROTECT,
                                related_name='to_user_expenses', null=True, blank=True)
    to_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return f'{self.expense_type}: {self.price}'


class PharmacyExpense(AbstractIncomeExpense):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    from_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    to_user = models.ForeignKey(CustomUser, on_delete=models.PROTECT,
                                related_name='pharmacy_expenses', null=True, blank=True)

    def __str__(self):
        return f'{self.expense_type}: {self.price}'

# class ExpenseHistory(Expense):
#     pharmacy_expense = models.ForeignKey(Expense, on_delete=models.PROTECT,
#                                          related_name='pharmacy_expenses_history')
