from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from api.v1.apps.reports.models import Report


class TransferMoneyType(models.Model):
    name = models.CharField(max_length=150)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name


class AbstractIncomeExpense(models.Model):
    creator = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    report = models.ForeignKey(Report, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    price = models.PositiveIntegerField()
    shift = models.PositiveSmallIntegerField(validators=[MaxValueValidator(3), MinValueValidator(1)])
    transfer_type = models.ForeignKey(TransferMoneyType, on_delete=models.PROTECT)
    desc = models.CharField(max_length=500, blank=True)
    second_name = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        self.desc = ' '.join(self.desc.split())
        self.second_name = ' '.join(self.second_name.split())
        super().save(*args, **kwargs)

    class Meta:
        abstract = True
