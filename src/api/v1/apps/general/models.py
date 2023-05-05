from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from api.v1.apps.companies.models import Company
from api.v1.apps.reports.models import Report


class TransferMoneyType(models.Model):
    name = models.CharField(max_length=150)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['name', 'company']


class IncomeExpenseType(models.Model):
    is_expense_type = models.BooleanField(default=True)
    name = models.CharField(max_length=300)
    desc = models.CharField(max_length=600, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['name', 'company', 'is_expense_type']

    def save(self, *args, **kwargs):
        self.desc = ' '.join(self.desc.split())
        super().save(*args, **kwargs)


class AbstractIncomeExpense(models.Model):
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    report = models.ForeignKey(Report, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    income_expense_type = models.ForeignKey(IncomeExpenseType, on_delete=models.PROTECT)
    price = models.FloatField(validators=[MinValueValidator(0)])
    shift = models.PositiveSmallIntegerField(validators=[MaxValueValidator(3), MinValueValidator(1)])

    desc = models.CharField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        self.desc = ' '.join(self.desc.split())
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
