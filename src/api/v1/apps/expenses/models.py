from django.db import models

from api.v1.apps.companies.services import text_normalize
from api.v1.apps.companies.models import AbstractIncomeExpense


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
    from_user = models.ForeignKey('accounts.CustomUser', on_delete=models.PROTECT, related_name='from_user_expenses')

    # select
    to_user = models.ForeignKey('accounts.CustomUser', on_delete=models.PROTECT,
                                related_name='to_user_expenses', null=True, blank=True)
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT, null=True)  # last
    # -------

    def __str__(self):
        return f'{self.expense_type}: {self.price}'


class PharmacyExpense(AbstractIncomeExpense):
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    from_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    to_user = models.ForeignKey('accounts.CustomUser', on_delete=models.PROTECT,
                                related_name='pharmacy_expenses', null=True, blank=True)

    def __str__(self):
        return f'{self.expense_type}: {self.price}'
