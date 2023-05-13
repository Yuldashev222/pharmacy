from django.db import models

from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.general.services import text_normalize
from api.v1.apps.pharmacies.models import Pharmacy
from api.v1.apps.general.models import AbstractIncomeExpense


class ExpenseType(models.Model):
    name = models.CharField(max_length=300)
    is_user_expense = models.BooleanField(default=False)
    desc = models.CharField(max_length=600, blank=True)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.desc = text_normalize(self.desc)
        self.name = text_normalize(self.name)
        super().save(*args, **kwargs)


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