from django.db import models

from api.v1.companies.models import AbstractIncomeExpense
from api.v1.companies.reports.models import AllPharmacyIncomeReportMonth


class PharmacyIncomeReportMonth(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.BigIntegerField(default=0)

    def __str__(self):
        return f'{self.pharmacy}: {self.price}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        obj, _ = AllPharmacyIncomeReportMonth.objects.get_or_create(year=self.year,
                                                                    month=self.month,
                                                                    director_id=self.pharmacy.director_id)

        price = PharmacyIncomeReportMonth.objects.filter(month=obj.month,
                                                         year=obj.year,
                                                         pharmacy__director_id=obj.director_id
                                                         ).aggregate(s=models.Sum('price'))['s']

        obj.price = price if price else 0
        obj.save()


class PharmacyIncome(AbstractIncomeExpense):
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.CASCADE)
    to_user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, related_name='pharmacy_incomes',
                                blank=True, null=True)

    def __str__(self):
        return f'{self.to_pharmacy}: {self.price}'
