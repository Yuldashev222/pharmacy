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


class ExpenseType(models.Model):
    name = models.CharField(max_length=300)
    desc = models.CharField(max_length=600, blank=True)
    company = models.ForeignKey(Company, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['name', 'company']

    def save(self, *args, **kwargs):
        self.desc = ' '.join(self.desc.split())
        super().save(*args, **kwargs)


class AbstractIncomeExpense(models.Model):
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    report = models.ForeignKey(Report, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.FloatField(validators=[MinValueValidator(0)])
    shift = models.PositiveSmallIntegerField(validators=[MaxValueValidator(3), MinValueValidator(1)])
    transfer_type = models.ForeignKey(TransferMoneyType, on_delete=models.PROTECT)
    desc = models.CharField(max_length=500, blank=True)

    def save(self, *args, **kwargs):
        self.desc = ' '.join(self.desc.split())
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
