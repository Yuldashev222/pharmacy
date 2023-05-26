from django.db import models

from api.v1.apps.companies.models import TransferMoneyType, AbstractIncomeExpense


class PharmacyIncomeReportMonth(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    year = models.IntegerField()
    month = models.IntegerField()
    price = models.IntegerField(default=0)
    receipt_price = models.IntegerField(default=0)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.pharmacy}: {self.price}'


class PharmacyIncomeReportDay(models.Model):
    pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    report_date = models.DateField()
    price = models.IntegerField(default=0)
    receipt_price = models.IntegerField(default=0)
    director = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.pharmacy}: {self.price}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        data = PharmacyIncomeReportDay.objects.filter(
            report_date__month=self.report_date.month
        ).aggregate(s=models.Sum('price'), rs=models.Sum('receipt_price'))
        price, receipt_price = data['s'], data['rs']
        obj = PharmacyIncomeReportMonth.objects.get_or_create(
            pharmacy_id=self.pharmacy_id, year=self.report_date.year,
            month=self.report_date.month, director_id=self.director_id
        )[0]
        obj.price = price if price else 0
        obj.receipt_price = receipt_price if receipt_price else 0
        obj.save()


class PharmacyIncome(AbstractIncomeExpense):
    to_pharmacy = models.ForeignKey('pharmacies.Pharmacy', on_delete=models.PROTECT)
    to_user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.PROTECT,
        related_name='pharmacy_incomes', blank=True, null=True
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        price = PharmacyIncome.objects.filter(report_date=self.report_date).aggregate(s=models.Sum('price'))['s']
        obj = PharmacyIncomeReportDay.objects.get_or_create(
            pharmacy_id=self.to_pharmacy_id,
            report_date=self.report_date,
            director_id=self.creator.director_id
        )[0]
        obj.price = price if price else 0
        obj.save()

    def __str__(self):
        return f'{self.to_pharmacy}: {self.price}'
