from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from api.v1.apps.reports.models import Report


class TransferMoneyType(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.name = ' '.join(self.name.split())
        super().save(*args, **kwargs)


class IncomeExpenseType(models.Model):
    is_expense_type = models.BooleanField(default=True)
    name = models.CharField(max_length=300)
    desc = models.CharField(max_length=600, blank=True)
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL,
                                null=True)  # directors

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = ' '.join(self.name.split())
        super().save(*args, **kwargs)


class AbstractIncomeExpense(models.Model):
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    report = models.ForeignKey(Report, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    income_expense_type = models.ForeignKey(IncomeExpenseType, on_delete=models.PROTECT)
    price = models.FloatField(validators=[MinValueValidator(0)])
    shift = models.PositiveSmallIntegerField(validators=[MaxValueValidator(3), MinValueValidator(1)])  # or auto

    desc = models.CharField(max_length=500, blank=True)

    class Meta:
        abstract = True
