from django.db import models

from api.v1.apps.companies.models import TransferMoneyType, AbstractIncomeExpense


class PharmacyIncomeReportDay(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    report_date = models.DateField()
    price = models.IntegerField(default=0)
    receipt_price = models.IntegerField(default=0)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.pharmacy}: {self.price}'


class PharmacyIncome(AbstractIncomeExpense):
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    to_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT,
        related_name='pharmacy_incomes', blank=True, null=True
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        price = PharmacyIncome.objects.filter(report_date=self.report_date).aggregate(s=models.Sum('price'))['s']
        PharmacyIncomeReportDay.objects.get_or_create(
            pharmacy_id=self.to_pharmacy_id,
            report_date=self.report_date,
            price=price,
            director_id=self.creator.director_id
        )

    def __str__(self):
        return f'{self.to_pharmacy}: {self.price}'
