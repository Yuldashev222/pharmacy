from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from api.v1.apps.reports.models import Report
from api.v1.apps.general.enums import PriceType
from api.v1.apps.accounts.models import CustomUser
from api.v1.apps.pharmacies.models import Pharmacy


class IncomeType(models.Model):
    # default to_pharmacy, debt
    name = models.CharField(max_length=300, unique=True)
    desc = models.CharField(max_length=600, blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)  # directors

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = ' '.join(self.name.split())
        super().save(*args, **kwargs)


class Income(models.Model):
    report = models.ForeignKey(Report, on_delete=models.PROTECT)
    income_type = models.ForeignKey(IncomeType, on_delete=models.PROTECT)
    desc = models.CharField(max_length=500, blank=True)
    price_type = models.CharField(max_length=1, choices=PriceType.choices())
    price = models.FloatField(validators=[MinValueValidator(0)])
    shift = models.PositiveSmallIntegerField(default=0, validators=[MaxValueValidator(3)])  # or auto
    created_at = models.DateTimeField(auto_now_add=True)
    to_pharmacy = models.ForeignKey(Pharmacy, on_delete=models.PROTECT)
    creator = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'{self.income_type}: {self.price} => {self.get_price_type_display()}'


class IncomeHistory(models.Model):
    updater = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    income = models.ForeignKey(Income, on_delete=models.CASCADE)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.income


class OldIncome(Income):
    income_history = models.ForeignKey(IncomeHistory, on_delete=models.CASCADE)
