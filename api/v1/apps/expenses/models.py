from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from api.v1.apps.firms.models import Firm
from api.v1.apps.reports.models import Report
from api.v1.apps.general.enums import PriceType
from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.pharmacies.models import Pharmacy


class ExpenseType(models.Model):
    # default to_manager, to_director, to_worker, to_firm, to_pharmacy, debt
    name = models.CharField(max_length=300, unique=True)
    desc = models.CharField(max_length=600, blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)  # directors

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = ' '.join(self.name.split())
        super().save(*args, **kwargs)


class Expense(models.Model):
    report = models.ForeignKey(Report, on_delete=models.PROTECT)
    expense_type = models.ForeignKey(ExpenseType, on_delete=models.PROTECT)
    desc = models.CharField(max_length=500, blank=True)
    price_type = models.CharField(max_length=1, choices=PriceType.choices())
    price = models.FloatField(validators=[MinValueValidator(0)])
    shift = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(3)])  # or auto
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    # select
    to_firm = models.ForeignKey(Firm, on_delete=models.PROTECT)
    to_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    # ------

    # select
    from_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    from_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    # ------

    def __str__(self):
        return f'{self.expense_type}: {self.price} => {self.get_price_type_display()}'


class ExpenseHistory(models.Model):
    updater = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.expense


class OldExpense(Expense):
    expense_history = models.ForeignKey(ExpenseHistory, on_delete=models.CASCADE)
